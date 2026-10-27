import { useState, useEffect } from "react";
import { 
  Zap, ShieldCheck, CheckCircle2, XCircle, ArrowRight, RotateCcw, 
  HelpCircle, Award, BookOpen, Clock, Sparkles, AlertTriangle, Lock
} from "lucide-react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";

export default function AdaptivePractice() {
  const navigate = useNavigate();
  const location = useLocation();

  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState("");
  const [roadmap, setRoadmap] = useState([]);
  const [mode, setMode] = useState("weak_topics"); // "weak_topics" | "mastery"
  const [selectedTopicId, setSelectedTopicId] = useState("");

  // Quiz State
  const [quizState, setQuizState] = useState("idle"); // "idle" | "loading" | "active" | "results"
  const [assessmentId, setAssessmentId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [resultsData, setResultsData] = useState(null);
  const [timerSec, setTimerSec] = useState(0);

  useEffect(() => {
    api.get("/courses").then((res) => {
      setCourses(res.data);
      if (res.data.length > 0) {
        setSelectedCourse(res.data[0].id);
      }
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      api.get(`/quiz/course/${selectedCourse}/roadmap`)
        .then((res) => {
          setRoadmap(res.data);
          if (res.data.length > 0) {
            setSelectedTopicId(res.data[0].topic_id);
          }
        })
        .catch(() => {});
    }
  }, [selectedCourse, resultsData]);

  // Timer loop when quiz is active
  useEffect(() => {
    let interval = null;
    if (quizState === "active") {
      interval = setInterval(() => setTimerSec((s) => s + 1), 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [quizState]);

  async function startQuiz() {
    setQuizState("loading");
    setTimerSec(0);
    setCurrentIdx(0);
    setAnswers({});
    setResultsData(null);

    try {
      if (mode === "weak_topics") {
        const { data } = await api.post(`/quiz/${selectedCourse}/weak-topics/start`);
        setAssessmentId(data.assessment_id);
        setQuestions(data.questions);
        setQuizState("active");
      } else {
        const { data } = await api.post(`/quiz/topic/${selectedTopicId}/mastery/start`);
        setAssessmentId(data.assessment_id);
        setQuestions(data.questions);
        setQuizState("active");
      }
    } catch (err) {
      alert(err.response?.data?.detail || "Could not launch quiz. Please take the diagnostic first.");
      setQuizState("idle");
    }
  }

  function selectOption(qId, optKey) {
    setAnswers((prev) => ({ ...prev, [qId]: optKey }));
  }

  async function handleSubmitQuiz() {
    setQuizState("loading");
    const payload = {
      assessment_id: assessmentId,
      answers: Object.entries(answers).map(([qId, opt]) => ({
        question_id: qId,
        selected_option: opt,
        time_taken_sec: Math.max(5, Math.floor(timerSec / (questions.length || 1))),
      })),
    };

    try {
      if (mode === "weak_topics") {
        const { data } = await api.post("/quiz/weak-topics/submit", payload);
        setResultsData(data);
        setQuizState("results");
      } else {
        const { data } = await api.post("/quiz/mastery/submit", payload);
        setResultsData(data);
        setQuizState("results");
      }
    } catch (err) {
      alert("Submission error. Please retry.");
      setQuizState("active");
    }
  }

  const currentQ = questions[currentIdx];
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
            Adaptive Practice & Mastery Gates
          </h1>
          <p className="text-slate-400 text-xs mt-0.5">
            Stage 2 weak-topic remediation drills & Stage 3 verified mastery gates (≥80% passing threshold).
          </p>
        </div>

        {courses.length > 0 && quizState === "idle" && (
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
      </div>

      {/* IDLE VIEW: Mode Selector & Topic Picker */}
      {quizState === "idle" && (
        <div className="space-y-6">
          <div className="grid sm:grid-cols-2 gap-4">
            <button
              onClick={() => setMode("weak_topics")}
              className={`p-5 rounded-2xl border text-left transition flex flex-col justify-between ${
                mode === "weak_topics"
                  ? "border-brand-500 bg-brand-500/10 shadow-lg shadow-brand-500/10"
                  : "border-white/10 bg-white/5 hover:bg-white/10"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300">
                    Stage 2
                  </span>
                  <Zap size={18} className="text-brand-400" />
                </div>
                <h3 className="text-base font-bold text-white">Weak-Topic Targeted Drill</h3>
                <p className="text-slate-400 text-xs mt-1.5 leading-relaxed">
                  Automatically extracts questions strictly from topics where your competency diagnostic scored in the Weak or Average tier.
                </p>
              </div>
              <span className="text-[11px] text-brand-300 font-semibold mt-4 block">
                Recommended for Gap Remediation →
              </span>
            </button>

            <button
              onClick={() => setMode("mastery")}
              className={`p-5 rounded-2xl border text-left transition flex flex-col justify-between ${
                mode === "mastery"
                  ? "border-accent-500 bg-accent-500/10 shadow-lg shadow-accent-500/10"
                  : "border-white/10 bg-white/5 hover:bg-white/10"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-accent-500/20 text-accent-300">
                    Stage 3
                  </span>
                  <ShieldCheck size={18} className="text-accent-400" />
                </div>
                <h3 className="text-base font-bold text-white">Single-Topic Mastery Gate</h3>
                <p className="text-slate-400 text-xs mt-1.5 leading-relaxed">
                  High-stakes gating assessment testing conceptual invariants, edge cases, and algorithmic analysis. Requires ≥80% score to unlock next module.
                </p>
              </div>
              <span className="text-[11px] text-accent-300 font-semibold mt-4 block">
                Verification & Badge Gating →
              </span>
            </button>
          </div>

          {/* If Mastery Gate selected: show topic curriculum roadmap */}
          {mode === "mastery" && (
            <GlassCard className="p-5 border-white/10">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <BookOpen size={16} className="text-brand-400" />
                Select Topic for Mastery Challenge:
              </h3>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {roadmap.map((t) => {
                  const isSelected = selectedTopicId === t.topic_id;
                  return (
                    <button
                      key={t.topic_id}
                      onClick={() => t.is_unlocked && setSelectedTopicId(t.topic_id)}
                      disabled={!t.is_unlocked}
                      className={`p-3.5 rounded-xl border text-left transition relative ${
                        isSelected
                          ? "border-accent-500 bg-accent-500/20"
                          : t.is_unlocked
                          ? "border-white/10 bg-white/5 hover:bg-white/10 text-slate-200"
                          : "border-white/5 bg-white/[0.02] opacity-40 cursor-not-allowed"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-white">{t.topic_name}</span>
                        {t.is_mastered ? (
                          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-500/20 text-emerald-300 font-bold">
                            Mastered
                          </span>
                        ) : !t.is_unlocked ? (
                          <Lock size={12} className="text-slate-500" />
                        ) : (
                          <span className="text-[10px] text-slate-400">{t.score_pct}%</span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-400">
                        {t.is_mastered ? "Gate cleared" : t.is_unlocked ? "Ready to test" : "Locked"}
                      </p>
                    </button>
                  );
                })}
              </div>
            </GlassCard>
          )}

          <div className="flex justify-center pt-2">
            <button
              onClick={startQuiz}
              className="btn-primary px-8 py-3.5 text-sm flex items-center gap-2"
            >
              <Zap size={16} />
              <span>Launch {mode === "weak_topics" ? "Weak-Topic Remediation Drill" : "Mastery Gate Assessment"}</span>
            </button>
          </div>
        </div>
      )}

      {/* LOADING VIEW */}
      {quizState === "loading" && (
        <div className="p-16 text-center text-slate-400 flex flex-col items-center gap-3">
          <Sparkles className="animate-spin text-brand-400" size={32} />
          <p className="font-medium text-slate-200">Generating adaptive questions using Bloom's taxonomy…</p>
          <p className="text-xs text-slate-500">Checking for unseen questions and calibrated difficulty.</p>
        </div>
      )}

      {/* ACTIVE QUIZ INTERFACE */}
      {quizState === "active" && currentQ && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded-md bg-brand-500/20 text-brand-300 font-bold uppercase text-[10px]">
                {currentQ.bloom_level || "Understand"}
              </span>
              <span>Question {currentIdx + 1} of {questions.length}</span>
            </div>
            <div className="flex items-center gap-1 font-mono">
              <Clock size={13} className="text-brand-400" />
              <span>{Math.floor(timerSec / 60)}:{(timerSec % 60).toString().padStart(2, "0")}</span>
            </div>
          </div>

          <div className="w-full h-1.5 rounded-full bg-white/5 overflow-hidden">
            <div
              className="h-full bg-brand-gradient transition-all duration-300"
              style={{ width: `${((currentIdx + 1) / questions.length) * 100}%` }}
            />
          </div>

          <GlassCard className="p-6">
            <h2 className="text-base sm:text-lg font-semibold text-white leading-relaxed mb-6">
              {currentQ.question_text}
            </h2>

            <div className="space-y-3">
              {Object.entries(currentQ.options).map(([key, text]) => {
                const isSelected = answers[currentQ.id] === key;
                return (
                  <button
                    key={key}
                    onClick={() => selectOption(currentQ.id, key)}
                    className={`w-full text-left p-3.5 rounded-xl border transition flex items-center gap-3 ${
                      isSelected
                        ? "border-brand-500 bg-brand-500/20 text-white shadow-md shadow-brand-500/10"
                        : "border-white/10 bg-white/5 hover:bg-white/10 text-slate-200"
                    }`}
                  >
                    <span className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs uppercase ${
                      isSelected ? "bg-brand-500 text-white" : "bg-white/10 text-slate-400"
                    }`}>
                      {key}
                    </span>
                    <span className="text-xs sm:text-sm">{text}</span>
                  </button>
                );
              })}
            </div>

            <div className="flex justify-between items-center mt-8 pt-4 border-t border-white/10">
              <button
                disabled={currentIdx === 0}
                onClick={() => setCurrentIdx((c) => c - 1)}
                className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 disabled:opacity-30 text-xs font-semibold text-slate-300 transition"
              >
                Previous
              </button>

              {currentIdx < questions.length - 1 ? (
                <button
                  onClick={() => setCurrentIdx((c) => c + 1)}
                  className="btn-primary text-xs py-2 px-5"
                >
                  Next Question
                </button>
              ) : (
                <button
                  onClick={handleSubmitQuiz}
                  disabled={answeredCount === 0}
                  className="btn-primary text-xs py-2 px-6 flex items-center gap-1.5"
                >
                  <CheckCircle2 size={14} />
                  <span>Submit Assessment ({answeredCount}/{questions.length})</span>
                </button>
              )}
            </div>
          </GlassCard>
        </div>
      )}

      {/* RESULTS & DIAGNOSTIC REVIEW SCREEN */}
      {quizState === "results" && resultsData && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <GlassCard className="p-6 text-center border-brand-500/30">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-gradient shadow-lg shadow-brand-500/30 mb-3">
              <Award className="text-white" size={28} />
            </div>

            <h2 className="text-2xl font-bold text-white">
              {resultsData.passed !== undefined
                ? resultsData.passed
                  ? "🎉 Mastery Achieved!"
                  : "Needs Further Practice"
                : "Remediation Drill Completed!"}
            </h2>
            <p className="text-slate-300 text-xs sm:text-sm max-w-lg mx-auto mt-2 leading-relaxed">
              {resultsData.message}
            </p>

            <div className="flex items-center justify-center gap-4 mt-5">
              {resultsData.score_pct !== undefined && (
                <div className="px-4 py-2 rounded-xl bg-white/5 border border-white/10">
                  <span className="text-[10px] text-slate-400 block uppercase font-bold">Accuracy</span>
                  <span className="text-xl font-bold text-brand-300">{resultsData.score_pct}%</span>
                </div>
              )}
              {resultsData.xp_awarded && (
                <div className="px-4 py-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
                  <span className="text-[10px] text-amber-400 block uppercase font-bold">XP Earned</span>
                  <span className="text-xl font-bold text-amber-300">+{resultsData.xp_awarded} XP</span>
                </div>
              )}
            </div>

            <div className="flex items-center justify-center gap-3 mt-6">
              <button
                onClick={() => setQuizState("idle")}
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-xs font-semibold text-slate-200 border border-white/10 transition"
              >
                Return to Practice Hub
              </button>
              <Link
                to="/student/tutor"
                className="btn-primary text-xs py-2 px-4 flex items-center gap-1.5"
              >
                <HelpCircle size={14} />
                <span>Ask AI Tutor About These Questions</span>
              </Link>
            </div>
          </GlassCard>

          {/* Question Breakdown with Explanations */}
          {resultsData.questions && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-white">
                Detailed Question Analysis & Explanation Review:
              </h3>
              <div className="space-y-3">
                {resultsData.questions.map((q, idx) => (
                  <GlassCard
                    key={idx}
                    className={`p-4 border ${
                      q.is_correct
                        ? "border-emerald-500/30 bg-emerald-500/[0.02]"
                        : "border-red-500/30 bg-red-500/[0.02]"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="flex items-center gap-2">
                        {q.is_correct ? (
                          <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                        ) : (
                          <XCircle size={16} className="text-red-400 shrink-0" />
                        )}
                        <h4 className="text-xs sm:text-sm font-semibold text-slate-200">
                          {q.question_text}
                        </h4>
                      </div>
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                        q.is_correct ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300"
                      }`}>
                        {q.is_correct ? "Correct" : "Incorrect"}
                      </span>
                    </div>

                    <div className="grid sm:grid-cols-2 gap-2 text-xs mb-3 text-slate-300">
                      <div className="p-2 rounded-lg bg-white/5">
                        <span className="text-[10px] text-slate-400 block">Your Answer:</span>
                        <span className="font-semibold uppercase">{q.student_answer || "None"}</span>
                      </div>
                      <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                        <span className="text-[10px] block opacity-80">Correct Answer:</span>
                        <span className="font-semibold uppercase">{q.correct_answer}</span>
                      </div>
                    </div>

                    <p className="text-slate-300 text-xs leading-relaxed bg-white/[0.02] p-2.5 rounded-lg border border-white/5">
                      💡 <span className="font-semibold text-slate-200">Explanation:</span> {q.explanation}
                    </p>
                  </GlassCard>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
