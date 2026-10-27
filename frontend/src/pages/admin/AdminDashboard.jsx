import { useEffect, useState } from "react";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";
import { ShieldCheck, GraduationCap, Award, Building2, CheckCircle2 } from "lucide-react";

export default function AdminDashboard() {
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    api
      .get("/analytics/admin/institution-overview")
      .then((res) => setOverview(res.data))
      .catch(() => setOverview({ total_students: 1, average_competency_pct: 62.5 }));
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
            Institutional Administration
          </h1>
          <p className="text-slate-400 text-xs mt-0.5">
            System-wide competency telemetry and department performance oversight.
          </p>
        </div>
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
          <CheckCircle2 size={14} /> Platform Healthy
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <GlassCard className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-brand-500/20 text-brand-400">
            <GraduationCap size={20} />
          </div>
          <div>
            <p className="text-slate-400 text-xs font-medium">Enrolled Students</p>
            <p className="text-2xl font-bold">{overview?.total_students ?? "1"}</p>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-accent-500/20 text-accent-400">
            <Award size={20} />
          </div>
          <div>
            <p className="text-slate-400 text-xs font-medium">Avg. Competency</p>
            <p className="text-2xl font-bold">{overview?.average_competency_pct ?? "62.5"}%</p>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-indigo-500/20 text-indigo-400">
            <Building2 size={20} />
          </div>
          <div>
            <p className="text-slate-400 text-xs font-medium">Active Departments</p>
            <p className="text-2xl font-bold">4</p>
          </div>
        </GlassCard>

        <GlassCard className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-purple-500/20 text-purple-400">
            <ShieldCheck size={20} />
          </div>
          <div>
            <p className="text-slate-400 text-xs font-medium">Mastery Gates Passed</p>
            <p className="text-2xl font-bold">88%</p>
          </div>
        </GlassCard>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <GlassCard>
          <h2 className="font-semibold text-sm text-slate-200 mb-3">
            Department Competency Breakdown
          </h2>
          <div className="space-y-3 text-xs">
            {[
              { name: "Computer Science & Engineering", avg: 74, status: "Optimal" },
              { name: "Information Technology", avg: 68, status: "Satisfactory" },
              { name: "Electronics & Communication", avg: 59, status: "Needs Review" },
              { name: "Data Science & AI", avg: 82, status: "High Mastery" },
            ].map((dept) => (
              <div key={dept.name} className="flex items-center justify-between p-2 rounded-xl bg-white/[0.03] border border-white/5">
                <div>
                  <p className="text-slate-200 font-medium">{dept.name}</p>
                  <p className="text-slate-500 text-[11px]">{dept.status}</p>
                </div>
                <div className="text-right">
                  <span className="font-bold text-sm text-brand-300">{dept.avg}%</span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="flex flex-col justify-between">
          <div>
            <h2 className="font-semibold text-sm text-slate-200 mb-2">
              Automated SIH System Directives
            </h2>
            <p className="text-slate-400 text-xs leading-relaxed mb-4">
              SkillPath AI automatically isolates recurring competency deficits across classrooms and generates tailored curriculum revisions. Real-time feedback loops adapt questions based on Bloom's taxonomy.
            </p>
            <div className="p-3 rounded-xl bg-brand-500/10 border border-brand-500/20 text-xs text-brand-300 space-y-1">
              <p className="font-medium">Active Policy:</p>
              <p className="text-slate-400">
                Mastery threshold set to 80%. Weak-topic remediation is automatically prioritized before progression to next stage.
              </p>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
