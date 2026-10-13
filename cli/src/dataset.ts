import { randomUUID } from "node:crypto";
import { mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import envPaths from "env-paths";
import { EnvHttpProxyAgent } from "undici";
import { z } from "zod";
import { unpackData } from "../../web/src/loadData.js";
import { CliError, type DatasetContext } from "./types.js";

const nonempty = z.string().min(1);
const finite = z.number().finite();
const nonnegative = finite.nonnegative();
const nullableNumber = nonnegative.nullable();
const date = z.iso.date();

const pointSchema = z.object({
  id: nonempty,
  plan_id: nonempty,
  plan: nonempty,
  plan_en: z.string().nullable().optional(),
  local_price: z.string().nullable().optional(),
  model: nonempty,
  model_display: nonempty,
  vendor: nonempty,
  channel: nonempty,
  label: nonempty,
  billing: z.enum(["subscription", "metered"]),
  confidence: z.enum(["high", "medium", "low"]),
  price_usd: nullableNumber,
  original_price: nullableNumber,
  currency: nonempty,
  monthly_yi: nullableNumber,
  monthly_tokens: nullableNumber,
  real_usd_per_mtok: nonnegative,
  unmetered: z.boolean().optional(),
  promo_until: date.nullable().optional(),
  list_blended_usd_per_mtok: nullableNumber,
  workload: z.string().optional(),
  plan_gen: z.string().optional(),
  // Provenance uses exact dates, month-only samples and date ranges.
  data_date: z.string().nullable().optional(),
  data_date_kind: z.enum(["sample", "official", "derived"]).nullable().optional(),
  data_date_from: z.string().nullable().optional(),
  list_price: z.object({
    cached: nonnegative,
    input: nonnegative,
    output: nonnegative,
    currency: nonempty,
  }).nullable().optional(),
  d: nullableNumber.optional(),
  tier: z.string().optional(),
  source: z.string(),
  source_en: z.string().optional(),
  note: z.string(),
  note_en: z.string().optional(),
  decision_note: z.string(),
  decision_note_en: z.string().optional(),
  evidence: z.array(z.object({ label: nonempty, url: nonempty })),
}).passthrough();

const configurationSchema = z.object({
  configuration_id: nonempty,
  board: nonempty,
  model: nonempty,
  variant: nonempty,
  score: finite,
  score_is_estimated: z.boolean().nullable().optional(),
  score_is_self_reported: z.boolean().nullable().optional(),
  agent_harness: z.string().nullable(),
  reasoning_effort: z.string().nullable(),
  service_mode: z.string().nullable(),
  score_low: finite.nullable(),
  score_high: finite.nullable(),
  source: z.string(),
  source_en: z.string().optional(),
  record_note_en: z.string().optional(),
  record_note_zh: z.string().optional(),
  archive: z.string().optional(),
  checked_at: date.optional(),
  mean_cost_usd_per_task: nullableNumber.optional(),
  median_cost_per_task_usd: nullableNumber.optional(),
  median_cost_usd_per_task: nullableNumber.optional(),
}).passthrough();

// Packed mappings inherit benchmark fields from configurations. Older external
// snapshots may include those fields; validate every provided field as well.
const mappingSchema = configurationSchema.omit({ model: true }).partial().extend({
  configuration_id: nonempty,
  point_id: nonempty,
  mapping_kind: nonempty,
  mapping_confidence: z.enum(["high", "medium", "low"]),
  mapping_note: z.string(),
  quota_effort_matched: z.boolean().nullable(),
}).passthrough();

const mixFraction = finite.min(0).max(1);
const tokenMix = z.object({
  cache: mixFraction,
  input: mixFraction,
  output: mixFraction,
}).passthrough().refine((mix) => Math.abs(mix.cache + mix.input + mix.output - 1) < 1e-9, {
  message: "Token mix fractions must sum to 1",
});
const anthropicMix = z.object({
  cache: mixFraction,
  cacheWrite: mixFraction,
  output: mixFraction,
}).passthrough().refine((mix) => Math.abs(mix.cache + mix.cacheWrite + mix.output - 1) < 1e-9, {
  message: "Token mix fractions must sum to 1",
});

const snapshotSchema = z.object({
  version: z.literal(1),
  generatedAt: date,
  points: z.array(pointSchema),
  configurations: z.array(configurationSchema),
  mappings: z.array(mappingSchema),
  boards: z.record(nonempty, z.object({
    name: nonempty,
    metric: nonempty,
    url: z.url(),
    snapshot: date,
  }).passthrough()),
  conventions: z.object({
    usdPerCny: finite.positive(),
    monthWeeks: finite.positive(),
    exchangeRate: z.object({
      date,
      source: nonempty,
      labelEn: nonempty,
      labelZh: nonempty,
    }).passthrough(),
    standardTokenMix: tokenMix,
    lowCacheTokenMix: tokenMix,
    anthropicTokenMix: anthropicMix,
  }).passthrough(),
}).passthrough().superRefine((data, ctx) => {
  const issue = (message: string, field: (string | number)[]) =>
    ctx.addIssue({ code: "custom", path: field, message });
  const points = new Map<string, typeof data.points[number]>();
  data.points.forEach((point, i) => {
    if (points.has(point.id)) issue(`Duplicate point ID: ${point.id}`, ["points", i, "id"]);
    points.set(point.id, point);
    if (point.id !== `${point.plan_id}::${point.model}`)
      issue("Point ID must match plan_id::model", ["points", i, "id"]);
    if (point.unmetered && (point.real_usd_per_mtok !== 0 || point.monthly_tokens !== null || point.monthly_yi !== null))
      issue("Unmetered points must have zero price and no token denominator", ["points", i]);
    if ((point.monthly_tokens === null) !== (point.monthly_yi === null))
      issue("Token allowance fields must both be null or numeric", ["points", i]);
    if (point.monthly_tokens !== null && point.monthly_yi !== null) {
      if (point.monthly_tokens <= 0 || point.monthly_yi <= 0)
        issue("Monthly allowance must be positive", ["points", i, "monthly_tokens"]);
      if (Math.abs(point.monthly_tokens - point.monthly_yi * 1e8) > 1)
        issue("monthly_tokens and monthly_yi disagree", ["points", i, "monthly_tokens"]);
    }
  });
  const configs = new Map<string, typeof data.configurations[number]>();
  data.configurations.forEach((config, i) => {
    if (configs.has(config.configuration_id))
      issue(`Duplicate configuration ID: ${config.configuration_id}`, ["configurations", i, "configuration_id"]);
    configs.set(config.configuration_id, config);
    if (!Object.hasOwn(data.boards, config.board))
      issue(`Unknown board: ${config.board}`, ["configurations", i, "board"]);
    if (config.score_low !== null && config.score_high !== null && config.score_low > config.score_high)
      issue("score_low must not exceed score_high", ["configurations", i, "score_low"]);
  });
  const mappingIds = new Set<string>();
  data.mappings.forEach((mapping, i) => {
    const key = JSON.stringify([mapping.point_id, mapping.configuration_id]);
    if (mappingIds.has(key)) issue("Duplicate point/configuration mapping", ["mappings", i]);
    mappingIds.add(key);
    const point = points.get(mapping.point_id);
    const config = configs.get(mapping.configuration_id);
    if (!point) issue(`Unknown point: ${mapping.point_id}`, ["mappings", i, "point_id"]);
    if (!config) issue(`Unknown configuration: ${mapping.configuration_id}`, ["mappings", i, "configuration_id"]);
    if (point && config && point.model !== config.model)
      issue("Mapping model does not match the referenced point", ["mappings", i, "configuration_id"]);
    if (config) {
      for (const field of Object.keys(configurationSchema.shape)) {
        if (field === "model") continue;
        if (Object.hasOwn(mapping, field) && mapping[field] !== config[field])
          issue(`Mapping ${field} disagrees with the referenced configuration`, ["mappings", i, field]);
      }
    }
  });
});

export const DATASET_URL = "https://realapipricing.com/data/site.json";
const bundledPath = fileURLToPath(new URL("../data/site.json", import.meta.url));
const cacheSchema = z.object({
  etag: z.string().regex(/^[^\r\n]*$/).nullable(),
  snapshot: z.unknown(),
});

function parseSnapshot(raw: unknown, location: string): DatasetContext["data"] {
  const parsed = snapshotSchema.safeParse(raw);
  if (!parsed.success) {
    const details = parsed.error.issues.slice(0, 5).map((issue) =>
      `${issue.path.join(".") || "dataset"}: ${issue.message}`,
    ).join("; ");
    throw new CliError(`Invalid dataset: ${location}. ${details}`, 1);
  }
  return unpackData(parsed.data);
}

async function loadFile(filename: string): Promise<DatasetContext["data"]> {
  let raw: unknown;
  try {
    raw = JSON.parse(await readFile(filename, "utf8"));
  } catch (error) {
    const message = error instanceof SyntaxError ? "Invalid JSON" : "Cannot read dataset";
    throw new CliError(`${message}: ${filename}. ${error instanceof Error ? error.message : String(error)}`, 1);
  }
  return parseSnapshot(raw, filename);
}

async function readCache(filename: string) {
  try {
    const cached = cacheSchema.parse(JSON.parse(await readFile(filename, "utf8")));
    return { etag: cached.etag, data: parseSnapshot(cached.snapshot, filename) };
  } catch {
    return null;
  }
}

async function saveCache(filename: string, snapshot: unknown, etag: string | null) {
  // Keep the validator and snapshot in one atomic write so concurrent commands
  // cannot pair a new ETag with an older dataset.
  const temporary = `${filename}.${randomUUID()}.tmp`;
  try {
    await mkdir(path.dirname(filename), { recursive: true });
    await writeFile(temporary, JSON.stringify({ etag, snapshot }));
    await rename(temporary, filename);
  } catch {
    // A read-only cache must not prevent queries from using valid remote data.
  } finally {
    await rm(temporary, { force: true }).catch(() => {});
  }
}

// Dependency injection is internal to the loader; it adds no CLI options.
interface LoadOptions {
  cachePath?: string;
  fetch?: typeof globalThis.fetch;
  timeoutMs?: number;
}

/** Revalidate online, then transparently fall back to last-good or bundled data. */
export async function loadDataset(file?: string, options: LoadOptions = {}): Promise<DatasetContext> {
  if (file !== undefined) {
    const filename = path.resolve(file);
    return { data: await loadFile(filename), source: "file", sourcePath: filename };
  }
  const cachePath = options.cachePath ?? path.join(envPaths("real-api-pricing", { suffix: "" }).cache, "site.json");
  const cached = await readCache(cachePath);
  let dispatcher: EnvHttpProxyAgent | undefined;
  try {
    if (process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy) {
      dispatcher = new EnvHttpProxyAgent();
    }
    const request = options.fetch ?? globalThis.fetch;
    const signal = AbortSignal.timeout(options.timeoutMs ?? 3_000);
    const get = (etag?: string | null) => {
      const init: RequestInit & { dispatcher?: EnvHttpProxyAgent } = {
        headers: etag ? { "If-None-Match": etag } : {}, signal, dispatcher,
      };
      return request(DATASET_URL, init);
    };
    let response = await get(cached?.etag);
    if (response.status === 304 && !cached) response = await get();
    if (response.status === 304 && cached) {
      return { data: cached.data, source: "cache", sourcePath: cachePath };
    }
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const snapshot: unknown = await response.json();
    const data = parseSnapshot(snapshot, DATASET_URL);
    await saveCache(cachePath, snapshot, response.headers.get("etag"));
    return { data, source: "remote", sourcePath: null };
  } catch {
    if (cached) return { data: cached.data, source: "cache", sourcePath: cachePath };
    return { data: await loadFile(bundledPath), source: "bundled", sourcePath: null };
  } finally {
    await dispatcher?.destroy();
  }
}
