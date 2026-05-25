import React from "react";
import { render, screen, fireEvent } from "../utils/test-utils";
import { describe, it, expect } from "vitest";
import ThemeToggle from "./ThemeToggle";

describe("ThemeToggle", () => {
  it("toggles the dark class on document element when clicked", () => {
    render(<ThemeToggle />);
    const button = screen.getByTestId("theme-toggle");

    // Initial click to turn on dark mode
    fireEvent.click(button);
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(localStorage.getItem("theme")).toBe("dark");

    // Second click to turn off dark mode
    fireEvent.click(button);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(localStorage.getItem("theme")).toBe("light");
  });
});
