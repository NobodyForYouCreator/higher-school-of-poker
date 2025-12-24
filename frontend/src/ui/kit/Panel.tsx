import React from "react";

export function Panel({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div {...props} className={["panel", className].filter(Boolean).join(" ")} />;
}

export function PanelHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div {...props} className={["panelHeader", className].filter(Boolean).join(" ")} />;
}

export function PanelTitle({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div {...props} className={["panelTitle", className].filter(Boolean).join(" ")} />;
}

export function PanelSubtitle({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div {...props} className={["panelSubtitle", className].filter(Boolean).join(" ")} />;
}

export function PanelBody({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div {...props} className={["panelBody", className].filter(Boolean).join(" ")} />;
}

