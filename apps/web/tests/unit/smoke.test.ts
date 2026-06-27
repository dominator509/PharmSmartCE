import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import Home from "../../app/page";

describe("home page", () => {
  it("renders the product name", () => {
    const html = renderToStaticMarkup(Home());

    expect(html).toContain("PharmSmartCE");
  });
});
