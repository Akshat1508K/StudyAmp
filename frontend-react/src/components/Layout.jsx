import React, { useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  LayoutDashboard,
  Upload,
  MessageCircleQuestion,
  FileText,
  ClipboardList,
  Layers,
  GraduationCap,
  BarChart3,
  LogOut,
  Menu,
  X,
  Bell,
  User,
} from 'lucide-react';
import './Layout.css';

const Layout = () => {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/upload', icon: Upload, label: 'Upload Documents' },
    { path: '/ask', icon: MessageCircleQuestion, label: 'Ask Question' },
    { path: '/summary', icon: FileText, label: 'Generate Summary' },
    { path: '/quiz/generate', icon: ClipboardList, label: 'Generate Quiz' },
    { path: '/flashcards', icon: Layers, label: 'Flashcards' },
    { path: '/study-plan', icon: GraduationCap, label: 'Study Plan' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
  ];

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="logo">
            <GraduationCap size={32} />
            {sidebarOpen && <span className="logo-text">StudyAmp AI</span>}
          </div>
        </div>

        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `nav-item ${isActive ? 'active' : ''}`
              }
            >
              <item.icon size={20} />
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="avatar">
              <User size={20} />
            </div>
            {sidebarOpen && (
              <div className="user-details">
                <div className="user-name">{user?.name}</div>
                <div className="user-email">{user?.email}</div>
              </div>
            )}
          </div>
          <button className="logout-btn" onClick={logout}>
            <LogOut size={20} />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className={`main-content ${sidebarOpen ? '' : 'expanded'}`}>
        {/* Top Header */}
        <header className="top-header">
          <button
            className="menu-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>

          <div className="header-title">
            <h1>Dashboard</h1>
            <p>Welcome back! Here's an overview of your learning progress.</p>
          </div>

          <div className="header-actions">
            <button className="icon-btn">
              <Bell size={20} />
              <span className="badge-dot"></span>
            </button>
            <div className="header-avatar">
              <User size={20} />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
