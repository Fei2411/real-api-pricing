const patchedPrototypes = new WeakSet<object>();

/**
 * Browser translation can replace React-owned text nodes and make later DOM operations fail.
 */
export function installTranslationGuard(
  proto: Pick<Node, "removeChild" | "insertBefore">,
): void {
  if (patchedPrototypes.has(proto)) return;

  const originalRemoveChild = proto.removeChild;
  proto.removeChild = function <T extends Node>(this: Node, child: T): T {
    if (child.parentNode !== this) {
      console.warn("React tried to remove a node that is no longer a child.");
      return child;
    }
    return originalRemoveChild.call(this, child) as T;
  };

  const originalInsertBefore = proto.insertBefore;
  proto.insertBefore = function <T extends Node>(
    this: Node,
    newNode: T,
    referenceNode: Node | null,
  ): T {
    if (referenceNode && referenceNode.parentNode !== this) {
      console.warn("React tried to insert before a node that is no longer a child.");
      return newNode;
    }
    return originalInsertBefore.call(this, newNode, referenceNode) as T;
  };

  patchedPrototypes.add(proto);
}
