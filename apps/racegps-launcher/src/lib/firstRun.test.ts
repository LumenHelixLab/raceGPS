import assert from "node:assert/strict";
import test from "node:test";
import { DEFAULT_SETTINGS } from "@racegps/launcher-settings";
import { initialRoute } from "./firstRun.ts";

test("first run goes to wizard", () => {
  assert.equal(initialRoute(DEFAULT_SETTINGS), "/wizard");
});

test("completed goes home", () => {
  assert.equal(
    initialRoute({ ...DEFAULT_SETTINGS, firstRunCompleted: true }),
    "/",
  );
});
