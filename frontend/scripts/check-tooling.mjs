import { createRequire } from "node:module";
import assert from "node:assert/strict";
import { ESLint } from "eslint";

const packageRequire = createRequire(import.meta.url);
const react = packageRequire("react/package.json").version;
const reactDom = packageRequire("react-dom/package.json").version;
assert.equal(react, reactDom, "React and React DOM must resolve to the same version");
assert.equal(Number(process.versions.node.split(".")[0]), 24, "Use the documented Node 24 runtime");

assert.ok(process.env.npm_config_user_agent?.startsWith("npm/11.9.0 "), "Run with the frozen npm 11.9.0 runtime");

// Exercise the old plugin APIs through the official compatibility adapter.
// A valid project alone would not prove that these rules still detect errors.
const eslint = new ESLint();
const results = await eslint.lintText(
  'import { memo } from "react"; export default memo(() => <div><img src="/x.png" /></div>);',
  { filePath: "features/tooling-negative-probe.tsx" },
);
const rules = new Set(results[0].messages.map((message) => message.ruleId));
for (const rule of ["react/display-name", "jsx-a11y/alt-text", "@next/next/no-img-element"]) {
  assert.ok(rules.has(rule), `Expected negative probe to detect ${rule}`);
}
console.log("Tooling compatibility: PASS; matched React runtimes and all three negative lint probes detected");
