import React from "react";

export type BadgeTone = "neutral" | "good" | "warn" | "bad";

export default function Badge({
  tone = "neutral",
  className,
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { tone?: BadgeTone }) {
  const classes = ["badge", `badge-${tone}`, className].filter(Boolean).join(" ");
  return <span {...props} className={classes} />;
}

