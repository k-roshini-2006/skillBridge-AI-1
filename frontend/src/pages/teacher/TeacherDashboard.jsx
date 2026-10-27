import { useEffect, useState } from "react";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";
import { BookOpen, Users, AlertTriangle, TrendingUp } from "lucide-react";

export default function TeacherDashboard() {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState("");
  const [heatmap, setHeatmap] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/courses")
      .then((res) => {
        setCourses(res.data);
        if (res.data.length > 0) {
          setSelectedCourse(res.data[0].id);
        }
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      api
        .get("/analytics/teacher/class-heatmap", { params: { course_id: selectedCourse } })
        .then((res) => setHeatmap(res.data))
        .catch(() => setHeatmap({}));
    }
  }, [selectedCourse]);

  const totalWeakCount = heatmap
    ? Object.values(heatmap).reduce((acc, c) => acc + (c.weak || 0), 0)
    : 0;

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
            Teacher Analytics Dashboard
          </h1>
          <p className="text-slate-400 text-xs mt-0.5">
            Real-time cohort competency heatmap and early intervention tracking.
          </p>
        </div>

        {courses.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Course:</span>
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="bg-white/5 border border-white/10 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              {courses.map((c) => (
                <option key={c.id} value={c.id} className="bg-slate-900 text-white">
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <GlassCard className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-indigo-500/20 text-indigo-400">
            <Users size={20} />
          </div>
          <div>
            <p className="text-slate-400 text-xs font-medium">Class Size</p>
            <p className="text-2xl font-bold">42 Students</p>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-emerald-500/20 text-emerald-400">
            <TrendingUp size={20} />
          </div>
          <div>
            <p className="text-slate-400 text-xs font-medium">Average Diagnostic</p>
            <p className="text-2xl font-bold">71.4%</p>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-rose-500/20 text-rose-400">
            <AlertTriangle size={20} />
          </div>
          <div>
            <p className="text-slate-400 text-xs font-medium">Gaps Needing Attention</p>
            <p className="text-2xl font-bold">{totalWeakCount} Topics</p>
          </div>
        </GlassCard>
      </div>

      <GlassCard>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-sm text-slate-200">
            Cohort Topic Mastery Heatmap
          </h2>
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500" /> Weak
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Average
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Strong
            </span>
          </div>
        </div>

        <div className="space-y-3">
          {heatmap &&
            Object.entries(heatmap).map(([topic, counts]) => {
              const total = (counts.weak || 0) + (counts.average || 0) + (counts.strong || 0);
              const weakPct = total ? Math.round((counts.weak / total) * 100) : 0;
              const avgPct = total ? Math.round((counts.average / total) * 100) : 0;
              const strongPct = total ? Math.round((counts.strong / total) * 100) : 0;

              return (
                <div key={topic} className="flex items-center gap-4 py-1">
                  <span className="w-36 text-xs text-slate-300 font-medium truncate">{topic}</span>
                  <div className="flex-1 h-3 rounded-full bg-white/5 overflow-hidden flex shadow-inner">
                    <div
                      className="bg-red-500/80 transition-all duration-500"
                      style={{ width: `${weakPct}%` }}
                      title={`Weak: ${counts.weak} (${weakPct}%)`}
                    />
                    <div
                      className="bg-amber-500/80 transition-all duration-500"
                      style={{ width: `${avgPct}%` }}
                      title={`Average: ${counts.average} (${avgPct}%)`}
                    />
                    <div
                      className="bg-emerald-500/80 transition-all duration-500"
                      style={{ width: `${strongPct}%` }}
                      title={`Strong: ${counts.strong} (${strongPct}%)`}
                    />
                  </div>
                  <span className="text-[11px] text-slate-500 w-24 text-right">
                    {counts.weak} weak / {total}
                  </span>
                </div>
              );
            })}

          {heatmap && Object.keys(heatmap).length === 0 && (
            <p className="text-slate-500 text-xs py-4 text-center">
              No competency score records yet for this course. Have students submit diagnostics to populate the heatmap.
            </p>
          )}
        </div>
      </GlassCard>
    </div>
  );
}
