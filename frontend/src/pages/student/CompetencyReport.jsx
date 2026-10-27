import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams, Link } from "react-router-dom";
import SkillRadar from "../../components/charts/SkillRadar.jsx";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";
import { ArrowLeft, RefreshCw, Zap } from "lucide-react";

const LEVEL_COLOR = {
  strong: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
  average: "text-amber-400 bg-amber-500/10 border-amber-500/30",
  weak: "text-red-400 bg-red-500/10 border-red-500/30",
};

export default function CompetencyReport() {
  const { state } = useLocation();
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(state?.report || null);
  const [loading, setLoading] = useState(!state?.report);

  useEffect(() => {
    if (!report && courseId) {
      setLoading(true);
      api
        .get(`/competency/${courseId}/report`)
        .then((res) => {
          setReport(res.data);
          setLoading(false);
        })
        .catch(() => {
          setLoading(false);
        });
    }
  }, [courseId, report]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center text-slate-400 flex flex-col items-center gap-3">
        <RefreshCw className="animate-spin text-brand-400" size={28} />
        <p>Loading competency report and radar analytics…</p>
      </div>
    );
  }

  if (!report || !report.results || report.results.length === 0) {
    return (
      <div className="max-w-md mx-auto p-8 text-center space-y-4">
        <GlassCard>
          <h2 className="text-lg font-bold">No Diagnostic Results Yet</h2>
          <p className="text-slate-400 text-sm mt-2 mb-4">
            Take the diagnostic quiz to map out your competency gaps and unlock personalized recommendations.
          </p>
          <Link
            to={`/student/course/${courseId}/diagnostic`}
            className="btn-primary inline-flex items-center gap-2 text-sm"
          >
            Start Diagnostic Quiz
          </Link>
        </GlassCard>
      </div>
    );
  }

  const radarData = report.results.map((r) => ({ topic: r.topic_name, score: r.score_pct }));
  const weakCount = report.results.filter((r) => r.level === "weak").length;
  const avgScore = Math.round(
    report.results.reduce((acc, curr) => acc + curr.score_pct, 0) / report.results.length
  );

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Link
            to="/student"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white mb-2 transition"
          >
            <ArrowLeft size={14} /> Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
            Competency Gap Analysis
          </h1>
          <p className="text-slate-400 text-xs mt-0.5">
            Topic-level mastery breakdown with AI-driven gap identification.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-right">
            <span className="text-[11px] text-slate-400 block">Overall Mastery</span>
            <span className="text-lg font-bold text-brand-300">{avgScore}%</span>
          </div>
          <Link
            to={`/student/course/${courseId}/diagnostic`}
            className="px-3.5 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-xs font-medium text-slate-200 border border-white/10 transition"
          >
            Retake Diagnostic
          </Link>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <GlassCard className="lg:col-span-1 flex flex-col justify-center">
          <h2 className="text-sm font-semibold text-slate-300 mb-2 text-center">
            Multi-Topic Skill Radar
          </h2>
          <SkillRadar data={radarData} />
          <p className="text-[11px] text-slate-500 text-center mt-2">
            Target: ≥80% for mastery gating
          </p>
        </GlassCard>

        <div className="lg:col-span-2 space-y-3">
          <h2 className="text-sm font-semibold text-slate-300">Detailed Topic Diagnosis</h2>
          <div className="grid sm:grid-cols-2 gap-3">
            {report.results.map((r) => (
              <GlassCard key={r.topic_id} className="p-4 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-sm text-slate-100">{r.topic_name}</h3>
                    <span
                      className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border ${
                        LEVEL_COLOR[r.level] || "text-slate-400"
                      }`}
                    >
                      {r.level}
                    </span>
                  </div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-2xl font-bold">{r.score_pct}%</span>
                    <span className="text-xs text-slate-500">
                      (Confidence {Math.round(r.confidence_score * 100)}%)
                    </span>
                  </div>
                  <p className="text-slate-300 text-xs leading-relaxed">{r.reason_text}</p>
                </div>

                <div className="pt-3 mt-3 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-400">
                  <span>Est. Study: <strong className="text-brand-300 font-semibold">{r.estimated_hours} hrs</strong></span>
                  <Link
                    to="/student/practice"
                    className="text-xs font-semibold text-brand-300 hover:text-white flex items-center gap-1 transition"
                  >
                    {r.level === "weak" ? "Remediate →" : "Mastery Gate →"}
                  </Link>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </div>

      {weakCount > 0 && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-red-500/10 via-brand-500/10 to-accent-500/10 border border-brand-500/20 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-500/20 text-red-400 flex items-center justify-center font-bold">
              {weakCount}
            </div>
            <div>
              <h4 className="font-semibold text-sm text-white">
                {weakCount} Weak {weakCount === 1 ? "Topic" : "Topics"} Identified
              </h4>
              <p className="text-slate-400 text-xs">
                Adaptive practice can target these exact concepts to boost your score to mastery.
              </p>
            </div>
          </div>
          <Link
            to="/student/practice"
            className="btn-primary whitespace-nowrap text-xs flex items-center gap-1.5"
          >
            <Zap size={14} /> Launch Adaptive Practice Drill
          </Link>
        </div>
      )}

    </div>
  );
}
