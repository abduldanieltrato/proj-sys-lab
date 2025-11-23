// src/pages/Exames.jsx
import { useEffect, useState } from 'react';
import { getExames, deleteExame } from '../services/api';

export default function Exames() {
    const [exames, setExames] = useState([]);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        const data = await getExames();
        setExames(data);
    };

    const handleDelete = async (id) => {
        if (confirm("Deseja realmente excluir este exame?")) {
            await deleteExame(id);
            fetchData();
        }
    };

    return (
        <div className="container">
            <h2>Exames</h2>
            <table className="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nome</th>
                        <th>Código</th>
                        <th>Setor</th>
                        <th>Ativo</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {exames.map(e => (
                        <tr key={e.id}>
                            <td>{e.id}</td>
                            <td>{e.nome}</td>
                            <td>{e.codigo}</td>
                            <td>{e.setor}</td>
                            <td>{e.activo ? "Sim" : "Não"}</td>
                            <td>
                                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(e.id)}>Excluir</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
