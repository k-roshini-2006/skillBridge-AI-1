import { useState, useEffect } from "react";
import { 
  Calendar, CheckCircle2, Clock, Sparkles, RefreshCw, AlertCircle, 
  BookOpen, PlayCircle, FileText, ArrowRight, Zap, Target
} from "lucide-react";
import { Link } from "react-router-dom";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";

const ACTIVITY_ICONS = {
  "Visual Concept Breakdown": PlayCircle,
  "Video Walkthrough & Animation": PlayCircle,
  "Code Implementation & Cheatsheet": FileText,
  "Light Concept Revision & Notes": FileText,
  "Adaptive Gap Practice Quiz": Zap,
  "Low-Stakes Micro Practice": Zap,
  "Core Theory & Mental Model": BookOpen,
  "Hands-on Problem Solving": Target,
  "Targeted Weak-Topic Remediation": Target,
  "Mastery Gate Readiness Assessment": Sparkles,
};

export default function LearningPath() {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState("");
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [xpNotice, setXpNotice] = useState(null);

  useEffect(() => {
    api.get("/courses").then((res) => {
      setCourses(res.data);
      if (res.data.length > 0) {
        setSelectedCourse(res.data[0].id);
      }
    }).catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      fetchPath(selectedCourse);
    }
  }, [selectedCourse]);

  function fetchPath(courseId) {
    setLoading(true);
    api.get("/learning-path", { params: { course_id: courseId } })
      .then((res) => {
        setLearningPath(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }

  async function handleRegenerate() {
    setRegenerating(true);
    try {
      const { data } = await api.post(`/learning-path/course/${selectedCourse}/generate`);
      setLearningPath(data);
    } catch {}
    setRegenerating(false);
  }

  async function toggleTask(taskId) {
    try {
      const { data } = await api.put(`/learning-path/daily/${taskId}/toggle-complete`);
      setLearningPath((prev) => ({
        ...prev,
        daily_plan: prev.daily_plan.map((t) =>
          t.id === taskId ? { ...t, completed: data.completed } : t
        ),
      }));

      if (data.completed) {
        setXpNotice("+50 XP Earned! Keep up the momentum 🚀");
        setTimeout(() => setXpNotice(null), 3000);
      }
    } catch {}
  }

  const completedCount = learningPath?.daily_plan?.filter((t) => t.completed).length || 0;
  const totalDaily = learningPath?.daily_plan?.length || 0;
  const progressPct = totalDaily ? Math.round((completedCount / totalDaily) * 100) : 0;

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
      {/* Toast Notification */}
      {xpNotice && (
        <div className="fixed top-20 right-6 z-50 px-4 py-2.5 rounded-xl bg-brand-600 text-white font-semibold text-xs shadow-2xl flex items-center gap-2 animate-in fade-in slide-in-from-top-3">
          <Zap size={15} className="fill-amber-300 text-amber-300" />
          <span>{xpNotice}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
            Personalized Adaptive Learning Path
          </h1>
          <p className="text-slate-400 text-xs mt-0.5">
            AI-scheduled daily & weekly roadmap tailored directly to your competency gaps.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {courses.length > 0 && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs">
              <span className="text-slate-400">Course:</span>
              <select
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(e.target.value)}
                className="bg-transparent text-slate-200 focus:outline-none text-xs font-semibold"
              >
                {courses.map((c) => (
                  <option key={c.id} value={c.id} className="bg-slate-900 text-white">
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="px-3.5 py-1.5 rounded-xl bg-brand-500/20 hover:bg-brand-500/30 text-brand-300 border border-brand-500/30 text-xs font-medium flex items-center gap-1.5 transition"
          >
            <RefreshCw size={13} className={regenerating ? "animate-spin" : ""} />
            <span>{regenerating ? "Recalibrating…" : "Recalibrate Path"}</span>
          </button>
        </div>
      </div>

      {/* Cognitive Load / Wellness Adaptation Alert Banner */}
      {learningPath?.wellness_adjustment && (
        <div className="p-3.5 rounded-2xl bg-brand-500/10 border border-brand-500/20 text-xs text-brand-300 flex items-center gap-3">
          <Sparkles size={16} className="text-brand-400 shrink-0" />
          <span>{learningPath.wellness_adjustment}</span>
        </div>
      )}

      {/* Daily Plan Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar size={18} className="text-brand-400" />
            <h2 className="text-sm font-semibold text-white">Today's Focus Schedule</h2>
            <span className="text-xs text-slate-400 font-medium">
              ({completedCount} of {totalDaily} completed)
            </span>
          </div>

          <div className="w-36 h-2 rounded-full bg-white/5 overflow-hidden">
            <div
              className="h-full bg-brand-gradient transition-all duration-500"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {learningPath?.daily_plan?.map((task) => {
            const Icon = ACTIVITY_ICONS[task.activity_type] || BookOpen;
            return (
              <GlassCard
                key={task.id}
                className={`p-4 flex flex-col justify-between border transition ${
                  task.completed
                    ? "border-emerald-500/30 bg-emerald-500/[0.04]"
                    : "border-white/10 hover:border-brand-500/40"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300">
                      {task.topic_name}
                    </span>
                    <span className="text-[11px] text-slate-400 flex items-center gap-1">
                      <Clock size={12} />
                      {task.time_slot}
                    </span>
                  </div>

                  <h3
                    className={`font-semibold text-sm mt-2 flex items-center gap-2 ${
                      task.completed ? "line-through text-slate-400" : "text-white"
                    }`}
                  >
                    <Icon size={16} className="text-brand-400 shrink-0" />
                    <span>{task.activity_type}</span>
                  </h3>
                  <p className="text-slate-400 text-xs mt-1">
                    Est. Duration: {task.estimated_minutes} mins
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between">
                  <button
                    onClick={() => toggleTask(task.id)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition ${
                      task.completed
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        : "bg-white/5 hover:bg-white/15 text-slate-300 border border-white/10"
                    }`}
                  >
                    <CheckCircle2 size={13} className={task.completed ? "text-emerald-400" : ""} />
                    <span>{task.completed ? "Done (+50 XP)" : "Mark Done"}</span>
                  </button>

                  <Link
                    to="/student/practice"
                    className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 font-medium transition"
                  >
                    Launch <ArrowRight size={13} />
                  </Link>
                </div>
              </GlassCard>
            );
          })}
        </div>
      </div>

      {/* Weekly Plan Progression */}
      <GlassCard className="p-5 border-white/10">
        <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
          <Target size={18} className="text-accent-400" />
          7-Day Master Learning Roadmap
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          {learningPath?.weekly_plan?.map((w, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-white/[0.03] border border-white/5 flex flex-col justify-between hover:border-brand-500/30 transition"
            >
              <div>
                <span className="text-[11px] font-bold text-brand-300 uppercase block mb-1">
                  {w.day_of_week}
                </span>
                <p className="text-xs font-semibold text-slate-200 line-clamp-1">
                  {w.topic_name}
                </p>
                <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                  {w.activity_type}
                </p>
              </div>

              <span className="text-[10px] text-slate-500 block mt-3 pt-2 border-t border-white/5">
                Stage {idx + 1}
              </span>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
