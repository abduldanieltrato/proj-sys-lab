// src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Pacientes from './pages/Pacientes';
import Exames from './pages/Exames';
import ExameCampos from './pages/ExameCampo';
import Requisicoes from './pages/Requisicoes';
import Resultados from './pages/Resultados';
// Import CSS
import './App.css';

export default function App() {
    return (
        <BrowserRouter>
            <Navbar />
            <div className="container mt-4">
                <Routes>
                    {/* Página inicial */}
                    <Route path="/" element={<Pacientes />} />

                    {/* Páginas para cada modelo */}
                    <Route path="/pacientes" element={<Pacientes />} />
                    <Route path="/exames" element={<Exames />} />
                    <Route path="/examecampos" element={<ExameCampos />} />
                    <Route path="/requisicoes" element={<Requisicoes />} />
                    <Route path="/resultados" element={<Resultados />} />

                    {/* Rota curinga (opcional) */}
                    <Route path="*" element={<h2>404 - Página não encontrada</h2>} />
                </Routes>
            </div>
        </BrowserRouter>
    );
}
