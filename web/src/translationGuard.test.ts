import assert from "node:assert/strict";
import test from "node:test";
import { installTranslationGuard } from "./translationGuard";

type FakeNode = { parentNode: FakeProto | null };
type FakeProto = {
  removeChild: (child: FakeNode) => FakeNode;
  insertBefore: (newNode: FakeNode, referenceNode: FakeNode | null) => FakeNode;
};

test("translation guard preserves valid DOM operations and ignores stale nodes", () => {
  const originalWarn = console.warn;
  console.warn = () => {};
  try {
    const calls: string[] = [];
    const proto: FakeProto = {
      removeChild(child) {
        calls.push("removeChild");
        return child;
      },
      insertBefore(newNode) {
        calls.push("insertBefore");
        return newNode;
      },
    };
    const parent = proto as unknown as FakeNode;
    const child: FakeNode = { parentNode: proto };
    const foreignChild: FakeNode = { parentNode: null };
    const inserted: FakeNode = { parentNode: null };
    const reference: FakeNode = { parentNode: proto };
    const foreignReference: FakeNode = { parentNode: null };

    installTranslationGuard(proto as unknown as Pick<Node, "removeChild" | "insertBefore">);

    assert.equal(proto.removeChild(child), child);
    assert.deepEqual(calls, ["removeChild"]);
    assert.equal(proto.removeChild(foreignChild), foreignChild);
    assert.deepEqual(calls, ["removeChild"]);
    assert.equal(proto.insertBefore(inserted, reference), inserted);
    assert.deepEqual(calls, ["removeChild", "insertBefore"]);
    assert.equal(proto.insertBefore(inserted, foreignReference), inserted);
    assert.deepEqual(calls, ["removeChild", "insertBefore"]);
    assert.equal(proto.insertBefore(inserted, null), inserted);
    assert.deepEqual(calls, ["removeChild", "insertBefore", "insertBefore"]);

    const wrappedRemoveChild = proto.removeChild;
    const wrappedInsertBefore = proto.insertBefore;
    installTranslationGuard(proto as unknown as Pick<Node, "removeChild" | "insertBefore">);
    assert.equal(proto.removeChild, wrappedRemoveChild);
    assert.equal(proto.insertBefore, wrappedInsertBefore);
    assert.equal(parent, proto);
  } finally {
    console.warn = originalWarn;
  }
});
