// src/pages/Resultados.jsx
import { useEffect, useState } from 'react';
import { getResultados, deleteResultado, gerarPdfResultado } from '../services/api';

export default function Resultados() {
    const [resultados, setResultados] = useState([]);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        const data = await getResultados();
        setResultados(data);
    };

    const handleDelete = async (id) => {
        if (confirm("Deseja realmente excluir este resultado?")) {
            await deleteResultado(id);
            fetchData();
        }
    };

    return (
        <div className="container">
            <h2>Resultados</h2>
            <table className="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Requisição</th>
                        <th>Exame</th>
                        <th>Valor</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {resultados.map(r => (
                        <tr key={r.id}>
                            <td>{r.id}</td>
                            <td>{r.requisicao_id}</td>
                            <td>{r.exame_nome}</td>
                            <td>{r.valor}</td>
                            <td>
                                <button className="btn btn-sm btn-primary me-2" onClick={() => gerarPdfResultado(r.id)}>PDF</button>
                                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(r.id)}>Excluir</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
