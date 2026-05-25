import React from "react";
import { render, screen } from "@testing-library/react";
import SkeletonLoader from "./SkeletonLoader";
import { describe, it, expect } from "vitest";

describe("SkeletonLoader", () => {
  it("renders the skeleton loader correctly", () => {
    render(<SkeletonLoader />);
    const skeletonLoader = screen.getByTestId("skeleton-loader");
    expect(skeletonLoader).toBeInTheDocument();
    expect(skeletonLoader).toHaveClass("animate-pulse");
  });
});
