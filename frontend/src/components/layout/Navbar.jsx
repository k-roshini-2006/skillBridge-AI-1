import { useState, useEffect, useRef } from "react";
import { 
  LogOut, Sparkles, User, Shield, GraduationCap, School, Bell, 
  Flame, Zap, BookOpen, Compass, Award, MessageSquare, Check, X, ChevronDown
} from "lucide-react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { useAuthStore } from "../../store/authStore.js";
import api from "../../lib/api.js";

export default function Navbar() {
  const { role, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const [stats, setStats] = useState({ xp_points: 1240, current_streak: 5 });
  const [notifications, setNotifications] = useState([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const notifRef = useRef(null);

  useEffect(() => {
    if (role === "student") {
      api.get("/gamification/stats")
        .then((res) => setStats(res.data))
        .catch(() => {});
      
      api.get("/notifications")
        .then((res) => setNotifications(res.data))
        .catch(() => {});
    }
  }, [role, location.pathname]);

  // Click outside listener for notifications dropdown
  useEffect(() => {
    function handleClickOutside(e) {
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setShowNotifs(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleLogout() {
    logout();
    navigate("/login");
  }

  async function markAllRead() {
    try {
      await api.post("/notifications/mark-all-read");
      setNotifications((prev) => prev.map((n) => ({ ...n, read_bool: true })));
    } catch {}
  }

  async function markOneRead(id) {
    try {
      await api.put(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read_bool: true } : n))
      );
    } catch {}
  }

  const unreadCount = notifications.filter((n) => !n.read_bool).length;

  const roleIcon = {
    student: GraduationCap,
    teacher: School,
    admin: Shield,
  }[role] || User;
  const RoleIconComponent = roleIcon;

  const studentLinks = [
    { label: "Dashboard", path: "/student" },
    { label: "Career Stage", path: "/student/career-stage" },
    { label: "Learning Path", path: "/student/learning-path" },
    { label: "Practice & Mastery", path: "/student/practice" },
    { label: "AI Tutor", path: "/student/tutor" },
    { label: "Study Hub", path: "/student/materials" },
    { label: "Achievements", path: "/student/achievements" },
  ];

  return (
    <header className="sticky top-0 z-50 backdrop-blur-xl bg-slate-950/70 border-b border-white/10 px-4 sm:px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        
        {/* Left: Brand Logo */}
        <Link to={`/${role || "login"}`} className="flex items-center gap-3 group shrink-0">
          <div className="w-10 h-10 rounded-xl bg-brand-gradient flex items-center justify-center shadow-lg shadow-brand-500/25 group-hover:scale-105 transition-transform">
            <Sparkles className="text-white" size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg bg-clip-text text-transparent bg-brand-gradient">
                SkillBridge AI
              </span>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
                SIH 2026
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden md:block">
              Career Readiness & Competency Engine
            </p>
          </div>
        </Link>


        {/* Center: Student Navigation Links */}
        {role === "student" && (
          <nav className="hidden lg:flex items-center gap-1 bg-white/[0.03] border border-white/5 rounded-2xl p-1 text-xs font-medium">
            {studentLinks.map((link) => {
              const active = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-3 py-1.5 rounded-xl transition ${
                    active
                      ? "bg-brand-500/20 text-brand-300 font-semibold border border-brand-500/30 shadow-sm"
                      : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>
        )}

        {/* Right: Gamification Badges, Notifications & Profile */}
        <div className="flex items-center gap-3">
          {role === "student" && (
            <>
              {/* Streak Badge */}
              <Link 
                to="/student/achievements" 
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-orange-500/15 border border-orange-500/30 text-orange-400 text-xs font-bold hover:bg-orange-500/25 transition"
                title="Active Study Streak"
              >
                <Flame size={15} className="fill-orange-500 text-orange-500 animate-pulse" />
                <span>{stats.current_streak}d</span>
              </Link>

              {/* XP Badge */}
              <Link 
                to="/student/achievements" 
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-brand-500/15 border border-brand-500/30 text-brand-300 text-xs font-bold hover:bg-brand-500/25 transition"
                title="Total XP Points"
              >
                <Zap size={14} className="fill-brand-400 text-brand-400" />
                <span>{stats.xp_points} XP</span>
              </Link>

              {/* Notifications Bell */}
              <div className="relative" ref={notifRef}>
                <button
                  onClick={() => setShowNotifs(!showNotifs)}
                  className="relative p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white transition"
                  title="Notifications"
                >
                  <Bell size={16} />
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 text-white rounded-full text-[10px] font-bold flex items-center justify-center animate-bounce">
                      {unreadCount}
                    </span>
                  )}
                </button>

                {/* Notifications Dropdown */}
                {showNotifs && (
                  <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-slate-900/95 backdrop-blur-2xl border border-white/10 shadow-2xl p-4 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="flex items-center justify-between pb-2 mb-3 border-b border-white/10">
                      <div className="flex items-center gap-2">
                        <Bell size={14} className="text-brand-400" />
                        <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                          Notifications
                        </h4>
                        {unreadCount > 0 && (
                          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-brand-500/20 text-brand-300">
                            {unreadCount} new
                          </span>
                        )}
                      </div>
                      {unreadCount > 0 && (
                        <button
                          onClick={markAllRead}
                          className="text-[11px] text-slate-400 hover:text-brand-300 transition"
                        >
                          Mark all read
                        </button>
                      )}
                    </div>

                    <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                      {notifications.map((n) => (
                        <div
                          key={n.id}
                          onClick={() => markOneRead(n.id)}
                          className={`p-2.5 rounded-xl border transition cursor-pointer text-xs ${
                            n.read_bool
                              ? "bg-white/[0.02] border-white/5 text-slate-400"
                              : "bg-brand-500/10 border-brand-500/20 text-slate-200 font-medium"
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <p className="leading-snug">{n.message}</p>
                            {!n.read_bool && (
                              <span className="w-2 h-2 rounded-full bg-brand-400 shrink-0 mt-1" />
                            )}
                          </div>
                          <span className="text-[10px] text-slate-500 block mt-1">
                            {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      ))}
                      {notifications.length === 0 && (
                        <p className="text-slate-500 text-xs text-center py-4">
                          No notifications at the moment.
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </>
          )}

          {/* User Role Tag */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs">
            <RoleIconComponent size={14} className="text-brand-400" />
            <span className="text-slate-300 capitalize font-medium">{role || "Guest"}</span>
          </div>

          {/* Sign Out */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 p-2 sm:px-3 sm:py-1.5 text-xs text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl border border-transparent hover:border-red-500/20 transition"
            title="Sign Out"
          >
            <LogOut size={15} />
            <span className="hidden sm:inline">Exit</span>
          </button>
        </div>
      </div>

      {/* Mobile Navigation Row */}
      {role === "student" && (
        <div className="lg:hidden mt-2 pt-2 border-t border-white/5 flex items-center justify-between gap-1 overflow-x-auto text-[11px] pb-1">
          {studentLinks.map((link) => {
            const active = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`px-2.5 py-1 rounded-lg whitespace-nowrap transition ${
                  active
                    ? "bg-brand-500/20 text-brand-300 font-semibold border border-brand-500/30"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
}
