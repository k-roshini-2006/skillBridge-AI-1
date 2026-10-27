import { useState } from "react";
import { useNavigate } from "react-router-dom";
import GlassCard from "../components/ui/GlassCard.jsx";
import api from "../lib/api.js";
import { useAuthStore } from "../store/authStore.js";
import { GraduationCap, School, Shield, Sparkles, UserCheck, ArrowRight } from "lucide-react";

const ROLES = [
  { key: "student", label: "Student", icon: GraduationCap },
  { key: "teacher", label: "Teacher", icon: School },
  { key: "admin", label: "Admin", icon: Shield },
];

const DEMO_ACCOUNTS = {
  student: { email: "student@skillpath.ai", password: "password123", role: "student" },
  teacher: { email: "teacher@skillpath.ai", password: "password123", role: "teacher" },
  admin: { email: "admin@skillpath.ai", password: "password123", role: "admin" },
};

export default function Login() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [role, setRole] = useState("student");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [regNumber, setRegNumber] = useState("");
  const [department, setDepartment] = useState("Computer Science");
  const [semester, setSemester] = useState(4);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();

  async function handleLoginWithCredentials(loginEmail, loginPassword, loginRole) {
    setError("");
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", {
        email: loginEmail,
        password: loginPassword,
        role: loginRole,
      });
      login(data.access_token, data.role, data.user_id);
      navigate(`/${data.role}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (isRegistering) {
      if (role === "student") {
        setLoading(true);
        try {
          const { data } = await api.post("/auth/register/student", {
            email,
            password,
            reg_number: regNumber || `REG-${Date.now().toString().slice(-5)}`,
            semester: Number(semester) || 1,
            department: department || "Computer Science",
          });
          login(data.access_token, data.role, data.user_id);
          navigate(`/${data.role}`);
        } catch (err) {
          setError(err.response?.data?.detail || "Registration failed.");
        } finally {
          setLoading(false);
        }
      } else {
        setError("Self-registration is available for Students. Please use Demo login for Teacher/Admin.");
      }
    } else {
      await handleLoginWithCredentials(email, password, role);
    }
  }

  function handleQuickDemo(demoRole) {
    const creds = DEMO_ACCOUNTS[demoRole];
    setRole(creds.role);
    setEmail(creds.email);
    setPassword(creds.password);
    setIsRegistering(false);
    handleLoginWithCredentials(creds.email, creds.password, creds.role);
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      {/* Background glow effects */}
      <div className="fixed top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-brand-600/15 rounded-full blur-3xl pointer-events-none" />

      <GlassCard className="w-full max-w-md relative z-10">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-gradient shadow-lg shadow-brand-500/30 mb-3">
            <Sparkles className="text-white" size={28} />
          </div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
            SkillBridge AI
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Adaptive Learning & Automatic Competency Gap Identification
          </p>
        </div>

        {/* Quick Demo Selector */}
        <div className="mb-6 p-3 rounded-xl bg-white/[0.03] border border-white/10">
          <p className="text-slate-400 text-[11px] font-medium uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <UserCheck size={13} className="text-brand-400" />
            1-Click Demo Logins
          </p>
          <div className="grid grid-cols-3 gap-2">
            {ROLES.map((r) => {
              const Icon = r.icon;
              return (
                <button
                  key={`demo-${r.key}`}
                  type="button"
                  onClick={() => handleQuickDemo(r.key)}
                  disabled={loading}
                  className="px-2 py-2 rounded-lg bg-white/5 hover:bg-brand-500/20 border border-white/5 hover:border-brand-500/40 text-xs text-slate-300 hover:text-white transition flex flex-col items-center gap-1"
                >
                  <Icon size={16} className="text-brand-400" />
                  <span className="font-semibold text-[11px]">{r.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Auth Mode Toggle */}
        <div className="flex rounded-xl bg-white/5 p-1 mb-5 border border-white/10 text-xs">
          <button
            type="button"
            onClick={() => { setIsRegistering(false); setError(""); }}
            className={`flex-1 py-1.5 rounded-lg font-medium transition ${
              !isRegistering
                ? "bg-brand-gradient text-white shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsRegistering(true); setError(""); }}
            className={`flex-1 py-1.5 rounded-lg font-medium transition ${
              isRegistering
                ? "bg-brand-gradient text-white shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Create Student Account
          </button>
        </div>

        {/* Role Tabs for Sign In */}
        {!isRegistering && (
          <div className="flex gap-2 mb-4">
            {ROLES.map((r) => {
              const Icon = r.icon;
              return (
                <button
                  key={r.key}
                  type="button"
                  onClick={() => setRole(r.key)}
                  className={`flex-1 py-2 px-2 rounded-xl text-xs font-medium transition flex items-center justify-center gap-1.5 ${
                    role === r.key
                      ? "bg-white/15 text-white border border-brand-400/30"
                      : "bg-white/5 text-slate-400 hover:bg-white/10"
                  }`}
                >
                  <Icon size={14} />
                  <span>{r.label}</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Auth Form */}
        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label className="block text-[11px] text-slate-400 mb-1">Email</label>
            <input
              type="email"
              placeholder={isRegistering ? "new.student@skillpath.ai" : "user@skillpath.ai"}
              className="input-field text-sm"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-[11px] text-slate-400 mb-1">Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="input-field text-sm"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {isRegistering && (
            <>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Roll / Reg #</label>
                  <input
                    type="text"
                    placeholder="CS2026-009"
                    className="input-field text-sm"
                    value={regNumber}
                    onChange={(e) => setRegNumber(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Semester</label>
                  <input
                    type="number"
                    min="1"
                    max="8"
                    placeholder="4"
                    className="input-field text-sm"
                    value={semester}
                    onChange={(e) => setSemester(e.target.value)}
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Department</label>
                <input
                  type="text"
                  placeholder="Computer Science"
                  className="input-field text-sm"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  required
                />
              </div>
            </>
          )}

          {error && (
            <div className="p-2.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-xs">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2 mt-2"
          >
            {loading ? (
              <span>Authenticating…</span>
            ) : isRegistering ? (
              <>
                <span>Register & Enter</span>
                <ArrowRight size={16} />
              </>
            ) : (
              <>
                <span>Sign in as {ROLES.find((r) => r.key === role)?.label}</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>
      </GlassCard>
    </div>
  );
}
