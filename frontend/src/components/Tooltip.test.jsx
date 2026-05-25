import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import Tooltip from "./Tooltip";

describe("Tooltip Component", () => {
  test("should not be visible by default", () => {
    render(
      <Tooltip text="Test tooltip">
        <span>Hover me</span>
      </Tooltip>,
    );
    expect(screen.queryByText("Test tooltip")).not.toBeInTheDocument();
  });

  test("should become visible on mouse enter", () => {
    render(
      <Tooltip text="Test tooltip">
        <span>Hover me</span>
      </Tooltip>,
    );
    const hoverTarget = screen.getByText("Hover me");
    fireEvent.mouseEnter(hoverTarget);
    expect(screen.getByText("Test tooltip")).toBeInTheDocument();
  });

  test("should hide on mouse leave", () => {
    render(
      <Tooltip text="Test tooltip">
        <span>Hover me</span>
      </Tooltip>,
    );
    const hoverTarget = screen.getByText("Hover me");
    fireEvent.mouseEnter(hoverTarget);
    expect(screen.getByText("Test tooltip")).toBeInTheDocument();
    fireEvent.mouseLeave(hoverTarget);
    expect(screen.queryByText("Test tooltip")).not.toBeInTheDocument();
  });
});
