import { useState, useEffect } from "react";
import { 
  Briefcase, Upload, FileText, CheckCircle2, AlertCircle, ArrowRight, 
  Sparkles, Award, Target, Zap, Bot, RefreshCw, ChevronRight, Layers, 
  Code, ShieldCheck, HelpCircle, ExternalLink, Flame
} from "lucide-react";
import { Link } from "react-router-dom";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";

const STAGES = [
  { num: 1, name: "Beginner", desc: "Basic theory, few demonstrated skills, no practical projects yet." },
  { num: 2, name: "Learner", desc: "Foundational skills, learning core technologies, building small exercises." },
  { num: 3, name: "Project Builder", desc: "Completed practical standalone projects with demonstrated job-relevant skills." },
  { num: 4, name: "Internship Ready", desc: "Robust portfolio, practical problem solving, ready to contribute in engineering teams." },
  { num: 5, name: "Job Ready", desc: "Strong end-to-end alignment, production-grade projects, industry experience." },
];

export default function CareerStageAssessment() {
  const [targetRoles, setTargetRoles] = useState([]);
  const [selectedRoleId, setSelectedRoleId] = useState("full-stack-developer");
  const [useCustomJob, setUseCustomJob] = useState(false);
  const [customJobDesc, setCustomJobDesc] = useState("");

  const [inputMode, setInputMode] = useState("upload"); // "upload" | "paste"
  const [file, setFile] = useState(null);
  const [resumeText, setResumeText] = useState("");

  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [xpNotice, setXpNotice] = useState(null);

  useEffect(() => {
    // Fetch target roles
    api.get("/career-stage/target-roles")
      .then((res) => setTargetRoles(res.data))
      .catch(() => {});

    // Fetch latest assessment if available
    api.get("/career-stage/latest")
      .then((res) => {
        if (res.data) setAssessment(res.data);
      })
      .catch(() => {});

    // Fetch history
    api.get("/career-stage/history")
      .then((res) => setHistory(res.data))
      .catch(() => {});
  }, []);

  async function handleAssess() {
    setLoading(true);
    setXpNotice(null);

    try {
      let data;
      if (inputMode === "upload") {
        if (!file) {
          alert("Please select a resume file (.pdf or .txt) to upload.");
          setLoading(false);
          return;
        }
        const formData = new FormData();
        formData.append("file", file);
        formData.append("target_role", selectedRoleId);
        if (useCustomJob && customJobDesc.trim()) {
          formData.append("job_description", customJobDesc);
        }
        const res = await api.post("/career-stage/assess-file", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        data = res.data;
      } else {
        if (!resumeText.trim()) {
          alert("Please paste your resume text.");
          setLoading(false);
          return;
        }
        const res = await api.post("/career-stage/assess-text", {
          resume_text: resumeText,
          target_role: selectedRoleId,
          job_description: useCustomJob ? customJobDesc : null,
        });
        data = res.data;
      }

      setAssessment(data);
      setXpNotice("+100 XP Earned! Career Stage Assessed 🎯");
      // Refresh history
      api.get("/career-stage/history").then((r) => setHistory(r.data)).catch(() => {});
    } catch (err) {
      alert(err.response?.data?.detail || "Assessment failed. Please verify your resume content.");
    } finally {
      setLoading(false);
    }
  }

  const selectedRole = targetRoles.find((r) => r.id === selectedRoleId) || targetRoles[0];

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-8">
      {/* XP Toast Notification */}
      {xpNotice && (
        <div className="fixed top-20 right-6 z-50 px-4 py-2.5 rounded-xl bg-brand-600 text-white font-semibold text-xs shadow-2xl flex items-center gap-2 animate-in fade-in slide-in-from-top-3">
          <Zap size={15} className="fill-amber-300 text-amber-300" />
          <span>{xpNotice}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
              AI Career Stage Assessment
            </h1>
            <span className="px-2.5 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 text-[11px] font-semibold">
              Stages 1 – 5
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Upload your resume to estimate your current career readiness stage, uncover missing skills, and unlock a step-by-step roadmap to job readiness.
          </p>
        </div>

        {history.length > 0 && (
          <div className="text-right">
            <span className="text-[11px] text-slate-400 block">Assessments Completed</span>
            <span className="text-sm font-bold text-slate-200">{history.length} evaluation(s)</span>
          </div>
        )}
      </div>

      {/* RESUME INPUT & ROLE CONFIGURATION SECTION */}
      <GlassCard className="p-6 border-white/10 space-y-6">
        <div>
          <h2 className="text-base font-bold text-white mb-1 flex items-center gap-2">
            <Briefcase size={18} className="text-brand-400" />
            Step 1: Select Target Job Role & Input Resume
          </h2>
          <p className="text-slate-400 text-xs">
            Career stage is evaluated relative to your target role. The same student may be at different readiness stages for different career tracks.
          </p>
        </div>

        {/* Target Role Selector */}
        <div>
          <label className="text-xs font-semibold text-slate-300 block mb-2">
            Target Job Role:
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {targetRoles.map((role) => {
              const active = selectedRoleId === role.id;
              return (
                <button
                  key={role.id}
                  type="button"
                  onClick={() => setSelectedRoleId(role.id)}
                  className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
                    active
                      ? "border-brand-500 bg-brand-500/20 text-white shadow-md shadow-brand-500/15"
                      : "border-white/10 bg-white/5 hover:bg-white/10 text-slate-300"
                  }`}
                >
                  <span className="text-xs font-bold block">{role.name}</span>
                  <span className="text-[10px] text-slate-400 mt-1">{role.category}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Custom Job Description Toggle */}
        <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-300">
              Optional: Match Against a Specific Job Posting Description
            </span>
            <button
              type="button"
              onClick={() => setUseCustomJob(!useCustomJob)}
              className="text-xs text-brand-300 hover:text-white font-semibold transition"
            >
              {useCustomJob ? "Hide Job Description" : "+ Add Job Description"}
            </button>
          </div>
          {useCustomJob && (
            <textarea
              rows={3}
              placeholder="Paste the job description or requirements here..."
              value={customJobDesc}
              onChange={(e) => setCustomJobDesc(e.target.value)}
              className="input-field text-xs font-mono"
            />
          )}
        </div>

        {/* Input Mode Toggle: File Upload vs Paste Text */}
        <div className="space-y-3">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setInputMode("upload")}
              className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition ${
                inputMode === "upload"
                  ? "bg-brand-500 text-white"
                  : "bg-white/5 text-slate-400 hover:text-white"
              }`}
            >
              <Upload size={14} /> Upload Resume (.PDF / .TXT)
            </button>
            <button
              type="button"
              onClick={() => setInputMode("paste")}
              className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition ${
                inputMode === "paste"
                  ? "bg-brand-500 text-white"
                  : "bg-white/5 text-slate-400 hover:text-white"
              }`}
            >
              <FileText size={14} /> Paste Resume Text
            </button>
          </div>

          {inputMode === "upload" ? (
            <div className="border-2 border-dashed border-white/10 hover:border-brand-500/50 rounded-2xl p-6 text-center transition bg-white/[0.01]">
              <Upload size={28} className="mx-auto text-brand-400 mb-2" />
              <label className="cursor-pointer">
                <span className="btn-primary text-xs py-1.5 px-4 inline-block mb-2">
                  Browse File
                </span>
                <input
                  type="file"
                  accept=".pdf,.txt"
                  className="hidden"
                  onChange={(e) => setFile(e.target.files[0])}
                />
              </label>
              <p className="text-xs text-slate-400 mt-1">
                {file ? (
                  <span className="font-semibold text-emerald-400">
                    Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                  </span>
                ) : (
                  "Supports PDF and plain text resume documents."
                )}
              </p>
            </div>
          ) : (
            <textarea
              rows={6}
              placeholder="Paste your full resume text here (Education, Technical Skills, Projects, Experience, Certifications)..."
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              className="input-field text-xs font-mono"
            />
          )}
        </div>

        {/* Submit Assessment Button */}
        <div className="flex justify-end pt-2">
          <button
            onClick={handleAssess}
            disabled={loading}
            className="btn-primary px-7 py-3 text-sm flex items-center gap-2"
          >
            {loading ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                <span>Analyzing Resume & Mapping Competency Stage…</span>
              </>
            ) : (
              <>
                <Sparkles size={16} />
                <span>Estimate Career Readiness Stage</span>
              </>
            )}
          </button>
        </div>
      </GlassCard>

      {/* ASSESSMENT RESULTS SECTION */}
      {assessment && (
        <div className="space-y-6 animate-in fade-in duration-300">
          {/* Stage Stepper Banner */}
          <GlassCard className="p-6 border-brand-500/30 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-brand-400 block mb-1">
                  Target Track: {assessment.target_role}
                </span>
                <div className="flex items-center gap-3">
                  <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    Stage {assessment.career_stage}: {assessment.stage_name}
                  </h2>
                  <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold text-xs">
                    {assessment.match_percentage}% Role Match
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="px-5 py-2.5 rounded-2xl bg-white/5 border border-white/10 text-right">
                  <span className="text-[10px] text-slate-400 block uppercase font-bold">
                    Career Readiness Score
                  </span>
                  <span className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
                    {assessment.readiness_score}
                    <span className="text-xs text-slate-400">/100</span>
                  </span>
                </div>
              </div>
            </div>

            {/* 5-Stage Stepper Progression */}
            <div className="space-y-2">
              <div className="grid grid-cols-5 gap-2 text-center text-xs">
                {STAGES.map((s) => {
                  const isCurrent = s.num === assessment.career_stage;
                  const isPast = s.num < assessment.career_stage;
                  return (
                    <div
                      key={s.num}
                      className={`p-2 rounded-xl border transition ${
                        isCurrent
                          ? "border-brand-500 bg-brand-500/25 text-white shadow-lg shadow-brand-500/20"
                          : isPast
                          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                          : "border-white/5 bg-white/[0.02] text-slate-500"
                      }`}
                    >
                      <div className="flex items-center justify-center gap-1 mb-1">
                        {isPast ? (
                          <CheckCircle2 size={12} className="text-emerald-400" />
                        ) : isCurrent ? (
                          <Sparkles size={12} className="text-brand-300" />
                        ) : null}
                        <span className="font-bold text-[11px]">Stage {s.num}</span>
                      </div>
                      <span className="text-[10px] block font-semibold truncate">{s.name}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Transparent Evaluation Reason */}
            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 text-xs text-slate-300 leading-relaxed">
              <span className="font-bold text-white block mb-1">
                Evaluation Rationale:
              </span>
              <p>{assessment.stage_reason}</p>
            </div>
          </GlassCard>

          {/* Detailed Multi-Dimensional Score Breakdown */}
          {assessment.score_breakdown && (
            <div className="grid sm:grid-cols-4 gap-4">
              {Object.entries(assessment.score_breakdown).map(([dim, data]) => (
                <GlassCard key={dim} className="p-4 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                      {dim} Score
                    </span>
                    <div className="flex items-baseline gap-1">
                      <span className="text-2xl font-bold text-white">{data.score}</span>
                      <span className="text-xs text-slate-500">/ {data.max} pts</span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
                      {data.description}
                    </p>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-white/5 overflow-hidden mt-3">
                    <div
                      className="h-full bg-brand-gradient"
                      style={{ width: `${(data.score / data.max) * 100}%` }}
                    />
                  </div>
                </GlassCard>
              ))}
            </div>
          )}

          {/* Skills Comparison: Demonstrated vs Missing */}
          <div className="grid md:grid-cols-2 gap-6">
            <GlassCard className="p-5 border-emerald-500/20">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-emerald-400" />
                  Demonstrated Target Skills ({assessment.demonstrated_skills?.length || 0})
                </h3>
              </div>
              <p className="text-slate-400 text-xs mb-3">
                Competencies detected and verified from your projects and coursework:
              </p>
              <div className="flex flex-wrap gap-1.5">
                {assessment.demonstrated_skills?.map((skill) => (
                  <span
                    key={skill}
                    className="px-2.5 py-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-medium"
                  >
                    ✓ {skill}
                  </span>
                ))}
                {(!assessment.demonstrated_skills || assessment.demonstrated_skills.length === 0) && (
                  <span className="text-slate-500 text-xs">No core skills matched yet.</span>
                )}
              </div>
            </GlassCard>

            <GlassCard className="p-5 border-rose-500/20">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <AlertCircle size={16} className="text-rose-400" />
                  Missing Skills for {assessment.target_role} ({assessment.missing_skills?.length || 0})
                </h3>
              </div>
              <p className="text-slate-400 text-xs mb-3">
                Skills required by industry job specs needed to reach the next readiness stage:
              </p>
              <div className="flex flex-wrap gap-1.5">
                {assessment.missing_skills?.map((skill) => (
                  <span
                    key={skill}
                    className="px-2.5 py-1 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs font-medium"
                  >
                    + {skill}
                  </span>
                ))}
                {(!assessment.missing_skills || assessment.missing_skills.length === 0) && (
                  <span className="text-emerald-400 text-xs font-semibold">
                    All core target skills demonstrated!
                  </span>
                )}
              </div>
            </GlassCard>
          </div>

          {/* Personalized Step-by-Step Progression Plan */}
          <GlassCard className="p-6 border-white/10 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Target size={18} className="text-brand-400" />
                  Personalized Progression Plan to Next Stage
                </h3>
                <p className="text-slate-400 text-xs mt-0.5">
                  Actionable roadmap bridging your skill gaps to qualify for {assessment.target_role} roles.
                </p>
              </div>

              <Link
                to="/student/tutor"
                className="px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-brand-300 hover:text-white border border-white/10 flex items-center gap-1.5 transition"
              >
                <Bot size={14} /> Ask AI Tutor About Gaps
              </Link>
            </div>

            {/* Recommended Projects to Build */}
            {assessment.progression_plan?.projects_to_build && (
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                  <Code size={14} className="text-accent-400" />
                  Recommended Portfolio Projects to Build:
                </h4>
                <div className="grid sm:grid-cols-2 gap-3">
                  {assessment.progression_plan.projects_to_build.map((proj, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl bg-white/[0.03] border border-white/5 hover:border-brand-500/30 transition flex flex-col justify-between"
                    >
                      <div>
                        <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-accent-500/20 text-accent-300 inline-block mb-2">
                          Unlocks {proj.target_stage_unlock}
                        </span>
                        <h5 className="text-sm font-semibold text-white">{proj.title}</h5>
                        <p className="text-slate-400 text-xs mt-1 leading-relaxed">
                          {proj.description}
                        </p>
                      </div>

                      <div className="mt-3 pt-2 border-t border-white/5 flex flex-wrap gap-1">
                        {proj.skills_involved?.map((s) => (
                          <span key={s} className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-slate-300">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommended Practice & Mastery Assessments */}
            <div className="space-y-3 pt-2 border-t border-white/10">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                <Zap size={14} className="text-brand-400" />
                Recommended SkillBridge AI Assessments:
              </h4>
              <div className="grid sm:grid-cols-2 gap-3">
                <div className="p-3.5 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-between">
                  <div>
                    <h5 className="text-xs font-bold text-white">Stage 2: Weak-Topic Practice Drill</h5>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Target and remediate identified skill gaps.
                    </p>
                  </div>
                  <Link
                    to="/student/practice"
                    className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1 whitespace-nowrap"
                  >
                    Start Drill <ArrowRight size={12} />
                  </Link>
                </div>

                <div className="p-3.5 rounded-xl bg-accent-500/10 border border-accent-500/20 flex items-center justify-between">
                  <div>
                    <h5 className="text-xs font-bold text-white">Stage 3: Mastery Gate Challenge</h5>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Verify algorithmic invariants at ≥ 80% threshold.
                    </p>
                  </div>
                  <Link
                    to="/student/practice"
                    className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1 whitespace-nowrap"
                  >
                    Take Gate <ArrowRight size={12} />
                  </Link>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}
