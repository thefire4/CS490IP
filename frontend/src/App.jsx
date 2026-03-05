import { Routes, Route } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import FilmDetailsPage from "./pages/FilmsDetailsPage";
import ActorDetailsPage from "./pages/ActorDetailsPage";
import FilmsSearchPage from "./pages/FilmsSearchPage";
import Navbar from "./components/NavBar";
import CustomersPage from "./pages/CustomersPage";
import CustomerDetailsPage from "./pages/CustomerDetailsPage";

export default function App() {
  return (
    <>
    <Navbar />
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "20px" }}>
    <Routes>
      <Route path="/" element={<LandingPage />} />

      <Route path="/films/:filmid" element={<FilmDetailsPage />} />
      <Route path="/actors/:actorID" element={<ActorDetailsPage />} />

      <Route path="/films-search" element={<FilmsSearchPage />} />
      <Route path="/customers" element={<CustomersPage />} />
      <Route path="/customers/:customerID" element={<CustomerDetailsPage />} />
    </Routes>
    </div>
    </>
  );
}
