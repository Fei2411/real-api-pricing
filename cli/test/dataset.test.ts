import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { DATASET_URL, loadDataset } from "../src/dataset.js";
import { CliError } from "../src/types.js";

const bundled = fileURLToPath(new URL("../data/site.json", import.meta.url));
const snapshotText = await readFile(bundled, "utf8");

async function withSnapshot(
  text: string,
  callback: (filename: string) => Promise<void>,
): Promise<void> {
  const directory = await mkdtemp(path.join(os.tmpdir(), "rap-dataset-"));
  try {
    const filename = path.join(directory, "snapshot.json");
    await writeFile(filename, text);
    await callback(filename);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}

function datasetError(message: RegExp) {
  return (error: unknown) => {
    assert.ok(error instanceof CliError);
    assert.equal(error.exitCode, 1);
    assert.match(error.message, message);
    return true;
  };
}

test("bundled data expands compressed mappings and preserves complete metadata", async () => {
  const original = JSON.parse(snapshotText);
  const context = await loadDataset(undefined, {
    cachePath: path.join(os.tmpdir(), `rap-missing-cache-${process.pid}`, "site.json"),
    fetch: async () => { throw new TypeError("Offline"); },
  });
  assert.equal(context.source, "bundled");
  assert.equal(context.sourcePath, null);
  assert.equal(context.data.version, 1);
  assert.equal(context.data.points.length, original.points.length);
  const mapping = context.data.mappings[0];
  const config = context.data.configurations.find((c) => c.configuration_id === mapping.configuration_id)!;
  assert.equal(mapping.board, config.board);
  assert.equal(mapping.score, config.score);
  assert.equal(mapping.variant, config.variant);
  assert.equal(mapping.reasoning_effort, config.reasoning_effort);
  assert.deepEqual(context.data.boards, original.boards);
  assert.deepEqual(context.data.conventions, original.conventions);
});

test("explicit path sets resolved source metadata", async () => {
  const relative = path.relative(process.cwd(), bundled);
  const context = await loadDataset(relative);
  assert.equal(context.source, "file");
  assert.equal(context.sourcePath, bundled);
});

test("I/O and JSON errors are actionable exit-1 errors", async () => {
  await assert.rejects(loadDataset("/tmp/rap-does-not-exist/snapshot.json"), datasetError(/Cannot read dataset.*snapshot\.json/s));
  await withSnapshot("{broken", async (filename) => {
    await assert.rejects(loadDataset(filename), datasetError(/Invalid JSON/));
  });
});

const invalidCases: [string, (data: ReturnType<typeof JSON.parse>) => void, RegExp][] = [
  ["invalid English source", (d) => { d.points[0].source_en = 7; }, /source_en/],
  ["invalid English benchmark note", (d) => { d.configurations[0].record_note_en = []; }, /record_note_en/],
  ["unsupported version", (d) => { d.version = 2; }, /version/],
  ["missing snapshot date", (d) => { delete d.generatedAt; }, /generatedAt/],
  ["invalid board snapshot date", (d) => { Object.values<{ snapshot: string }>(d.boards)[0].snapshot = "yesterday"; }, /snapshot/],
  ["missing convention", (d) => { delete d.conventions.standardTokenMix; }, /standardTokenMix/],
  ["bad token mix", (d) => { d.conventions.standardTokenMix.cache = 0.5; }, /fractions must sum/],
  ["nonpositive exchange rate", (d) => { d.conventions.usdPerCny = 0; }, /usdPerCny/],
  ["nonnumeric price", (d) => { d.points[0].real_usd_per_mtok = "cheap"; }, /real_usd_per_mtok/],
  ["negative price", (d) => { d.points[0].real_usd_per_mtok = -1; }, /real_usd_per_mtok/],
  ["duplicate point", (d) => { d.points.push(d.points[0]); }, /Duplicate point ID/],
  ["bad point ID", (d) => { d.points[0].plan_id = "wrong_plan"; }, /Point ID must match/],
  ["mismatched token denominator", (d) => { d.points[0].monthly_tokens += 100; }, /monthly_tokens and monthly_yi disagree/],
  ["bad unmetered semantics", (d) => { d.points[0].unmetered = true; }, /Unmetered points/],
  ["duplicate configuration", (d) => { d.configurations.push(d.configurations[0]); }, /Duplicate configuration ID/],
  ["orphan board", (d) => { d.configurations[0].board = "missing-board"; }, /Unknown board/],
  ["orphan point", (d) => { d.mappings[0].point_id = "missing-point"; }, /Unknown point/],
  ["orphan configuration", (d) => { d.mappings[0].configuration_id = "missing-configuration"; }, /Unknown configuration/],
  ["duplicate mapping", (d) => { d.mappings.push(d.mappings[0]); }, /Duplicate point\/configuration mapping/],
  ["conflicting mapping board", (d) => { d.mappings[0].board = "wrong-board"; }, /Mapping board disagrees/],
  ["conflicting mapping score", (d) => { d.mappings[0].score = -999; }, /Mapping score disagrees/],
  ["bad mapping flag", (d) => { d.mappings[0].quota_effort_matched = "true"; }, /quota_effort_matched/],
  ["mapping model mismatch", (d) => { d.configurations.find((c: { configuration_id: string }) => c.configuration_id === d.mappings[0].configuration_id).model = "wrong-model"; }, /Mapping model does not match/],
];

for (const [name, mutate, message] of invalidCases) {
  test(`rejects ${name}`, async () => {
    const data = JSON.parse(snapshotText);
    mutate(data);
    await withSnapshot(JSON.stringify(data), async (filename) => {
      await assert.rejects(loadDataset(filename), datasetError(message));
    });
  });
}

test("rejects nonfinite numbers parsed from valid JSON exponent syntax", async () => {
  const data = JSON.parse(snapshotText);
  data.configurations[0].score = "NONFINITE_MARKER";
  const text = JSON.stringify(data).replace('"NONFINITE_MARKER"', "1e999");
  await withSnapshot(text, async (filename) => {
    await assert.rejects(loadDataset(filename), datasetError(/configurations\.0\.score/));
  });
});

test("accepts complete mapping fields when they agree with the shared configuration", async () => {
  const data = JSON.parse(snapshotText);
  const mapping = data.mappings[0];
  const config = data.configurations.find((c: { configuration_id: string }) => c.configuration_id === mapping.configuration_id);
  Object.assign(mapping, { board: config.board, score: config.score, variant: config.variant });
  await withSnapshot(JSON.stringify(data), async (filename) => {
    assert.equal((await loadDataset(filename)).data.mappings[0].score, config.score);
  });
});

async function withCache(callback: (cachePath: string) => Promise<void>) {
  const directory = await mkdtemp(path.join(os.tmpdir(), "rap-cache-"));
  try {
    await callback(path.join(directory, "site.json"));
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}

const offline: typeof fetch = async () => { throw new TypeError("Offline"); };

test("valid remote data replaces cache and revalidates with its ETag", async () => {
  await withCache(async (cachePath) => {
    const snapshot = { ...JSON.parse(snapshotText), generatedAt: "2027-01-02" };
    const fresh = await loadDataset(undefined, { cachePath, fetch: async (url, init) => {
      assert.equal(url, DATASET_URL);
      assert.equal(new Headers(init?.headers).get("if-none-match"), null);
      return Response.json(snapshot, { headers: { etag: '"snapshot-2"' } });
    } });
    assert.equal(fresh.source, "remote");
    assert.equal(fresh.sourcePath, null);
    assert.equal(fresh.data.generatedAt, snapshot.generatedAt);
    assert.deepEqual(JSON.parse(await readFile(cachePath, "utf8")), { etag: '"snapshot-2"', snapshot });
    const unchanged = await loadDataset(undefined, { cachePath, fetch: async (_url, init) => {
      assert.equal(new Headers(init?.headers).get("if-none-match"), '"snapshot-2"');
      return new Response(null, { status: 304 });
    } });
    assert.equal(unchanged.source, "cache");
    assert.equal(unchanged.sourcePath, cachePath);
    assert.deepEqual(unchanged.data, fresh.data);
    assert.equal((await loadDataset(undefined, { cachePath, fetch: offline })).data.generatedAt, snapshot.generatedAt);
  });
});

test("invalid remote responses preserve the last-good cache", async () => {
  await withCache(async (cachePath) => {
    const snapshot = { ...JSON.parse(snapshotText), generatedAt: "2027-01-03" };
    const envelope = JSON.stringify({ etag: '"last-good"', snapshot });
    await writeFile(cachePath, envelope);
    for (const request of [offline,
      async () => new Response("Unavailable", { status: 503 }),
      async () => new Response("invalid JSON"),
      async () => Response.json({ ...snapshot, version: 2 }),
    ]) {
      const context = await loadDataset(undefined, { cachePath, fetch: request });
      assert.equal(context.source, "cache");
      assert.equal(context.data.generatedAt, snapshot.generatedAt);
      assert.equal(await readFile(cachePath, "utf8"), envelope);
    }
  });
});

test("missing or invalid caches fall back to bundled data without poisoning requests", async () => {
  await withCache(async (cachePath) => {
    for (const content of [null, "{broken", JSON.stringify({ etag: '"bad"', snapshot: { version: 2 } }),
      JSON.stringify({ etag: "invalid\r\nheader", snapshot: JSON.parse(snapshotText) }),
    ]) {
      if (content !== null) await writeFile(cachePath, content);
      const context = await loadDataset(undefined, { cachePath, fetch: async (_url, init) => {
        assert.equal(new Headers(init?.headers).get("if-none-match"), null);
        throw new TypeError("Offline");
      } });
      assert.equal(context.source, "bundled");
      assert.equal(context.sourcePath, null);
      assert.equal(context.data.generatedAt, JSON.parse(snapshotText).generatedAt);
    }
  });
});

test("304 without a usable cache retries once without a conditional header", async () => {
  await withCache(async (cachePath) => {
    let requests = 0;
    const context = await loadDataset(undefined, { cachePath, fetch: async (_url, init) => {
      assert.equal(new Headers(init?.headers).get("if-none-match"), null);
      return ++requests === 1 ? new Response(null, { status: 304 }) : new Response(snapshotText);
    } });
    assert.equal(context.source, "remote");
    assert.equal(requests, 2);
  });
});

test("responses without an ETag remain usable offline and refresh unconditionally", async () => {
  await withCache(async (cachePath) => {
    await loadDataset(undefined, { cachePath, fetch: async () => new Response(snapshotText) });
    assert.equal(JSON.parse(await readFile(cachePath, "utf8")).etag, null);
    assert.equal((await loadDataset(undefined, { cachePath, fetch: offline })).source, "cache");
    await loadDataset(undefined, { cachePath, fetch: async (_url, init) => {
      assert.equal(new Headers(init?.headers).get("if-none-match"), null);
      return new Response(snapshotText);
    } });
  });
});

test("an unwritable cache still permits remote data and leaves no temporary files", async () => {
  await withCache(async (cachePath) => {
    await writeFile(cachePath, "parent is a file");
    const context = await loadDataset(undefined, { cachePath: path.join(cachePath, "site.json"),
      fetch: async () => new Response(snapshotText),
    });
    assert.equal(context.source, "remote");
    assert.equal(await readFile(cachePath, "utf8"), "parent is a file");
  });
});

test("request and body timeouts fall back to cached data", async () => {
  await withCache(async (cachePath) => {
    await writeFile(cachePath, JSON.stringify({ etag: null, snapshot: JSON.parse(snapshotText) }));
    const abort = (signal: AbortSignal) => new Promise<never>((_resolve, reject) => {
      // The timer keeps this mock alive while native AbortSignal.timeout is unref'ed.
      const timer = setTimeout(() => reject(new Error("Abort was not delivered")), 1_000);
      signal.addEventListener("abort", () => { clearTimeout(timer); reject(signal.reason); }, { once: true });
    });
    for (const waitForBody of [false, true]) {
      const context = await loadDataset(undefined, { cachePath, timeoutMs: 10, fetch: async (_url, init) => {
        const signal = init!.signal!;
        if (!waitForBody) return await abort(signal);
        const response = new Response(snapshotText);
        response.json = () => abort(signal);
        return response;
      } });
      assert.equal(context.source, "cache");
    }
  });
});

test("explicit local data bypasses the transport and cache", async () => {
  const context = await loadDataset(bundled, { cachePath: "/does/not/exist", fetch: async () => {
    assert.fail("explicit file must not fetch");
  } });
  assert.equal(context.source, "file");
});
