import React from "react";
import { render, screen, fireEvent } from "../utils/test-utils";
import { describe, it, expect } from "vitest";
import Header from "./Header";
import i18n from "../i18n";

describe("Header", () => {
  it("renders in default language (English) correctly", () => {
    render(<Header />);
    expect(screen.getByTestId("header-title")).toBeInTheDocument();
  });

  it("changes language to Polish when PL button is clicked", async () => {
    render(<Header />);
    const plButton = screen.getByText("PL");
    fireEvent.click(plButton);
    expect(i18n.language).toContain("pl");
  });

  it("changes language back to English when EN button is clicked", async () => {
    render(<Header />);
    const enButton = screen.getByText("EN");
    fireEvent.click(enButton);
    expect(i18n.language).toContain("en");
  });
});
