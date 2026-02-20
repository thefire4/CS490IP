import { Routes, Route } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import FilmDetailsPage from "./pages/FilmsDetailsPage";
import ActorDetailsPage from "./pages/ActorDetailsPage";
import FilmsSearchPage from "./pages/FilmsSearchPage";
import Navbar from "./components/NavBar";

export default function App() {
  return (
    <>
      <Navbar />
    
    <Routes>
      {/* landing */}
      <Route path="/" element={<LandingPage />} />

      {/* keep these EXACTLY (your working clickable routes) */}
      <Route path="/films/:filmid" element={<FilmDetailsPage />} />
      <Route path="/actors/:actorID" element={<ActorDetailsPage />} />

      {/* search page (separate path so it doesn't mess with /films/:filmId) */}
      <Route path="/films-search" element={<FilmsSearchPage />} />
    </Routes>
    </>
  );
}
