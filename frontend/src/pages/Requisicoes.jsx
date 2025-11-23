// src/pages/Requisicoes.jsx
import { useEffect, useState } from 'react';
import { getRequisicoes, deleteRequisicao, gerarPdfRequisicao } from '../services/api';

export default function Requisicoes() {
    const [requisicoes, setRequisicoes] = useState([]);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        const data = await getRequisicoes();
        setRequisicoes(data);
    };

    const handleDelete = async (id) => {
        if (confirm("Deseja realmente excluir esta requisição?")) {
            await deleteRequisicao(id);
            fetchData();
        }
    };

    return (
        <div className="container">
            <h2>Requisições</h2>
            <table className="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Paciente</th>
                        <th>Data</th>
                        <th>Status</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {requisicoes.map(r => (
                        <tr key={r.id}>
                            <td>{r.id}</td>
                            <td>{r.paciente_nome}</td>
                            <td>{new Date(r.data).toLocaleDateString()}</td>
                            <td>{r.status}</td>
                            <td>
                                <button className="btn btn-sm btn-primary me-2" onClick={() => gerarPdfRequisicao(r.id)}>PDF</button>
                                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(r.id)}>Excluir</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
