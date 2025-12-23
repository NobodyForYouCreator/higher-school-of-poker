import React from "react";

export type SegOption<T extends string> = {
  value: T;
  label: string;
};

export default function Segmented<T extends string>({
  value,
  options,
  onChange,
}: {
  value: T;
  options: SegOption<T>[];
  onChange: (value: T) => void;
}) {
  return (
    <div className="segmented" role="tablist">
      {options.map((o) => (
        <button
          key={o.value}
          className={o.value === value ? "segBtn segBtnActive" : "segBtn"}
          onClick={() => onChange(o.value)}
          type="button"
          role="tab"
          aria-selected={o.value === value}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

