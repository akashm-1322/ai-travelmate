import { Sparkles } from "lucide-react";

export default function FeaturePlaceholder({
  title,
  description,
}) {
  return (
    <div className="flex min-h-[70vh] items-center justify-center p-6">
      <div className="max-w-xl text-center">
        <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-400">
          <Sparkles size={28} />
        </div>

        <h1 className="text-3xl font-bold">
          {title}
        </h1>

        <p className="mt-4 text-slate-400">
          {description}
        </p>

        <div className="mt-6 rounded-xl border border-white/10 bg-white/[0.03] p-4 text-sm text-slate-500">
          Frontend foundation ready.
          <br />
          This module will be connected to the AI TravelMate
          backend in the next implementation step.
        </div>
      </div>
    </div>
  );
}