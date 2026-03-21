import { NavLink, Route, Routes } from 'react-router-dom'

import './App.css'
import { AdminPage } from './pages/AdminPage'
import { PublicPage } from './pages/PublicPage'

function App() {
  return (
    <div className="shell">
      <header className="hero">
        <div className="hero__brand">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
          <h1>UMaT Navigator</h1>
        </div>
        <nav className="hero__nav">
          <NavLink to="/" className="hero__link">
            Assistant
          </NavLink>
          <NavLink to="/admin" className="hero__link">
            Admin Console
          </NavLink>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<PublicPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </div>
  )
}

export default App
