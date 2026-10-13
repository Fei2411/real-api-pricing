import { appendFileSync, readFileSync } from "node:fs";

// Only compiled CLI tests import this module; production has no test transport options.
globalThis.fetch = async (input, init) => {
  const url = input instanceof Request ? input.url : String(input);
  const headers = new Headers(init?.headers ?? (input instanceof Request ? input.headers : undefined));
  if (process.env.RAP_TEST_FETCH_CALLS) {
    appendFileSync(process.env.RAP_TEST_FETCH_CALLS, JSON.stringify({
      url, etag: headers.get("if-none-match"),
    }) + "\n");
  }
  if (url !== "https://realapipricing.com/data/site.json") {
    throw new Error(`Unexpected test fetch URL: ${url}`);
  }
  switch (process.env.RAP_TEST_FETCH_MODE) {
    case "fresh":
      return new Response(readFileSync(process.env.RAP_TEST_SNAPSHOT, "utf8"), {
        status: 200,
        headers: { etag: '"cli-test-snapshot"', "content-type": "application/json" },
      });
    case "not-modified":
      return new Response(null, { status: 304 });
    case "http-error":
      return new Response("Service unavailable", { status: 503 });
    default:
      throw new TypeError("Test-only network outage");
  }
};
