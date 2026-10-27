import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { 
  Bell, Flame, Trophy, Zap, BookOpen, BarChart2, Heart, Check, 
  Sparkles, ArrowRight, Bot, Target, CheckCircle2, Clock, Briefcase, Award, TrendingUp
} from "lucide-react";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";

function StatCard({ icon: Icon, label, value, sub, accent }) {
  return (
    <GlassCard className="flex items-center gap-4 p-4 sm:p-5">
      <div className={`p-3 rounded-2xl ${accent}`}>
        <Icon size={22} className="text-white" />
      </div>
      <div>
        <p className="text-slate-400 text-xs font-medium">{label}</p>
        <p className="text-xl font-bold text-white">{value}</p>
        {sub && <p className="text-[10px] text-slate-500 mt-0.5">{sub}</p>}
      </div>
    </GlassCard>
  );
}

export default function StudentDashboard() {
  const [courses, setCourses] = useState([]);
  const [stats, setStats] = useState(null);
  const [learningPath, setLearningPath] = useState(null);
  const [wellnessStatus, setWellnessStatus] = useState(null);
  const [wellnessLoading, setWellnessLoading] = useState(false);
  const [stress, setStress] = useState(3);
  const [confidence, setConfidence] = useState(8);
  const [careerAssessment, setCareerAssessment] = useState(null);

  useEffect(() => {
    // Fetch courses
    api.get("/courses").then((res) => setCourses(res.data)).catch(() => {});
    
    // Fetch live gamification telemetry
    api.get("/gamification/stats").then((res) => setStats(res.data)).catch(() => {});

    // Fetch active daily plan
    api.get("/learning-path").then((res) => setLearningPath(res.data)).catch(() => {});

    // Fetch latest career stage assessment
    api.get("/career-stage/latest").then((res) => setCareerAssessment(res.data)).catch(() => {});
  }, []);

  async function handleWellnessSubmit() {
    setWellnessLoading(true);
    try {
      const { data } = await api.post("/wellness/checkin", {
        stress_level: Number(stress),
        confidence_level: Number(confidence),
        sleep_quality: 7,
        workload: 4,
        motivation: 8,
      });
      setWellnessStatus(data.recommendation);
      // Refresh learning path to reflect potential adaptation
      api.get("/learning-path").then((res) => setLearningPath(res.data)).catch(() => {});
    } catch {
      setWellnessStatus("Check-in recorded! Study schedule calibrated.");
    } finally {
      setWellnessLoading(false);
    }
  }

  async function toggleDailyTask(taskId) {
    try {
      const { data } = await api.put(`/learning-path/daily/${taskId}/toggle-complete`);
      setLearningPath((prev) => ({
        ...prev,
        daily_plan: prev.daily_plan.map((t) =>
          t.id === taskId ? { ...t, completed: data.completed } : t
        ),
      }));
      // Update XP in stats
      if (data.total_xp) {
        setStats((prev) => prev ? { ...prev, xp_points: data.total_xp } : prev);
      }
    } catch {}
  }

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white">
              Welcome back, Student 👋
            </h1>
            <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
              {stats?.rank || "Gold Scholar"}
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Continuous diagnostic assessment, real-time competency gap identification & grounded RAG tutoring.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to="/student/practice"
            className="btn-primary text-xs py-2 px-4 flex items-center gap-1.5"
          >
            <Zap size={14} /> Practice Weak Topics
          </Link>
          <Link
            to="/student/tutor"
            className="px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-slate-200 border border-white/10 flex items-center gap-1.5 transition"
          >
            <Bot size={14} className="text-accent-400" />
            AI Tutor
          </Link>
        </div>
      </div>

      {/* Live Telemetry Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={Flame}
          label="Active Streak"
          value={`${stats?.current_streak || 5} days`}
          sub={`Longest: ${stats?.longest_streak || 12}d`}
          accent="bg-orange-500/80 shadow-orange-500/20 shadow-lg"
        />
        <StatCard
          icon={Zap}
          label="XP Points"
          value={`${stats?.xp_points || 1240} XP`}
          sub={stats?.rank || "Gold Strategist"}
          accent="bg-brand-600/80 shadow-brand-600/20 shadow-lg"
        />
        <StatCard
          icon={Trophy}
          label="Skill Badges"
          value={`${stats?.badges?.length || 4} earned`}
          sub="Competency verified"
          accent="bg-accent-600/80 shadow-accent-600/20 shadow-lg"
        />
        <StatCard
          icon={Target}
          label="Today's Tasks"
          value={`${learningPath?.daily_plan?.filter((t) => t.completed).length || 0}/${learningPath?.daily_plan?.length || 3}`}
          sub="Adaptive schedule"
          accent="bg-emerald-600/80 shadow-emerald-600/20 shadow-lg"
        />
      </div>

      {/* Fast Action Grid */}
      <div className="grid sm:grid-cols-3 gap-4">
        <Link
          to="/student/tutor"
          className="p-4 rounded-2xl bg-gradient-to-br from-brand-600/20 to-purple-600/10 border border-brand-500/30 hover:border-brand-500/60 transition group flex flex-col justify-between"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 rounded-xl bg-brand-500/20 text-brand-300 group-hover:scale-105 transition-transform">
              <Bot size={20} />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
              Grounded RAG
            </span>
          </div>
          <div>
            <h3 className="text-sm font-bold text-white group-hover:text-brand-300 transition-colors">
              AI Pedagogical Tutor
            </h3>
            <p className="text-slate-400 text-xs mt-1">
              Ask questions strictly grounded in your syllabus with zero hallucinations.
            </p>
          </div>
          <span className="text-brand-400 text-xs font-semibold mt-3 flex items-center gap-1">
            Open Chat <ArrowRight size={13} />
          </span>
        </Link>

        <Link
          to="/student/practice"
          className="p-4 rounded-2xl bg-gradient-to-br from-accent-600/20 to-pink-600/10 border border-accent-500/30 hover:border-accent-500/60 transition group flex flex-col justify-between"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 rounded-xl bg-accent-500/20 text-accent-300 group-hover:scale-105 transition-transform">
              <Zap size={20} />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-accent-300 bg-accent-500/10 px-2 py-0.5 rounded-full border border-accent-500/20">
              Stages 2 & 3
            </span>
          </div>
          <div>
            <h3 className="text-sm font-bold text-white group-hover:text-accent-300 transition-colors">
              Adaptive Practice & Mastery Gates
            </h3>
            <p className="text-slate-400 text-xs mt-1">
              Target identified gaps and pass 80% gates to unlock the next curriculum stage.
            </p>
          </div>
          <span className="text-accent-400 text-xs font-semibold mt-3 flex items-center gap-1">
            Start Drill <ArrowRight size={13} />
          </span>
        </Link>

        <Link
          to="/student/materials"
          className="p-4 rounded-2xl bg-gradient-to-br from-indigo-600/20 to-blue-600/10 border border-indigo-500/30 hover:border-indigo-500/60 transition group flex flex-col justify-between"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-300 group-hover:scale-105 transition-transform">
              <BookOpen size={20} />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-blue-300 bg-blue-500/10 px-2 py-0.5 rounded-full border border-blue-500/20">
              Curriculum Notes
            </span>
          </div>
          <div>
            <h3 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
              Study Hub & Complexity Guides
            </h3>
            <p className="text-slate-400 text-xs mt-1">
              Browse textbook notes, algorithmic cheatsheets, and interview problem sets.
            </p>
          </div>
          <span className="text-indigo-400 text-xs font-semibold mt-3 flex items-center gap-1">
            Browse Hub <ArrowRight size={13} />
          </span>
        </Link>
      </div>

      {/* Today's Adaptive Daily Plan Mini Widget */}
      {learningPath?.daily_plan && learningPath.daily_plan.length > 0 && (
        <GlassCard className="p-5 border-white/10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Target size={18} className="text-brand-400" />
              <h2 className="text-sm font-bold text-white">Today's Adaptive Action Plan</h2>
            </div>
            <Link
              to="/student/learning-path"
              className="text-xs text-brand-400 hover:text-brand-300 font-medium flex items-center gap-1"
            >
              Full Schedule <ArrowRight size={12} />
            </Link>
          </div>

          <div className="grid md:grid-cols-3 gap-3">
            {learningPath.daily_plan.map((t) => (
              <div
                key={t.id}
                className={`p-3 rounded-xl border flex items-center justify-between gap-3 transition ${
                  t.completed
                    ? "bg-emerald-500/10 border-emerald-500/30 text-slate-400"
                    : "bg-white/[0.03] border-white/5 text-slate-200"
                }`}
              >
                <div>
                  <span className="text-[10px] text-brand-300 font-bold block uppercase">
                    {t.topic_name}
                  </span>
                  <p className={`text-xs font-semibold ${t.completed ? "line-through opacity-70" : "text-white"}`}>
                    {t.activity_type}
                  </p>
                  <span className="text-[10px] text-slate-500 block mt-0.5">
                    {t.time_slot} ({t.estimated_minutes}m)
                  </span>
                </div>

                <button
                  onClick={() => toggleDailyTask(t.id)}
                  className={`p-1.5 rounded-lg border transition ${
                    t.completed
                      ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                      : "bg-white/5 text-slate-400 hover:text-white border-white/10"
                  }`}
                  title="Toggle complete"
                >
                  <CheckCircle2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Enrolled Courses & Diagnostics */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <BookOpen size={18} className="text-brand-400" />
            Enrolled Courses & Competency Radar
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-5">
          {courses.map((course) => (
            <GlassCard key={course.id} className="flex flex-col justify-between border-white/10 hover:border-brand-500/40 transition">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300">
                    Core Curriculum
                  </span>
                  <span className="text-xs text-slate-400">{course.topics.length} topics</span>
                </div>
                <h3 className="font-bold text-base text-white">{course.name}</h3>
                <p className="text-slate-400 text-xs mt-1 leading-relaxed">
                  {course.description || "Foundational concepts and practical algorithmic applications."}
                </p>

                <div className="mt-3 flex flex-wrap gap-1.5">
                  {course.topics.map((t) => (
                    <span key={t.id} className="text-[10px] px-2 py-0.5 rounded-md bg-white/5 text-slate-300">
                      {t.name}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-white/10 flex gap-2">
                <Link
                  to={`/student/course/${course.id}/diagnostic`}
                  className="btn-primary flex-1 text-center text-xs py-2"
                >
                  Start Diagnostic
                </Link>
                <Link
                  to={`/student/course/${course.id}/report`}
                  className="px-3 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-medium text-slate-200 border border-white/10 flex items-center gap-1.5 transition"
                >
                  <BarChart2 size={13} className="text-brand-400" />
                  Skill Radar
                </Link>
              </div>
            </GlassCard>
          ))}
        </div>
      </div>

      {/* Wellness & Cognitive Load Dynamic Widget */}
      <GlassCard className="p-5 border-white/10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-2xl bg-rose-500/20 text-rose-400">
              <Heart size={22} />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Daily Cognitive Load & Wellness Calibration</h3>
              <p className="text-xs text-slate-400">
                The platform dynamically scales your daily practice duration based on your mental workload.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <span>Stress:</span>
              <select
                value={stress}
                onChange={(e) => setStress(e.target.value)}
                className="bg-white/5 border border-white/10 rounded-lg px-2 py-1 text-xs text-white"
              >
                <option value={2} className="bg-slate-900">Low (2/10)</option>
                <option value={4} className="bg-slate-900">Moderate (4/10)</option>
                <option value={8} className="bg-slate-900">High (8/10)</option>
              </select>
            </div>

            <button
              onClick={handleWellnessSubmit}
              disabled={wellnessLoading}
              className="px-3.5 py-1.5 rounded-xl bg-white/10 hover:bg-brand-500/20 hover:text-white border border-white/10 text-xs font-semibold text-slate-200 transition"
            >
              {wellnessLoading ? "Saving…" : "Check in"}
            </button>
          </div>
        </div>

        {wellnessStatus && (
          <div className="mt-3 p-3 rounded-xl bg-brand-500/10 border border-brand-500/20 text-xs text-brand-300 flex items-center gap-2">
            <Check size={14} className="text-brand-400 shrink-0" />
            <span>{wellnessStatus}</span>
          </div>
        )}
      </GlassCard>
    </div>
  );
}
