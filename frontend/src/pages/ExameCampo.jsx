// src/pages/ExameCampo.jsx
import { useEffect, useState } from 'react';
import { getExameCampos, deleteExameCampo } from '../services/api';

export default function ExameCampo() {
    const [exameCampos, setExameCampos] = useState([]);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        const data = await getExameCampos();
        setExameCampos(data);
    };

    const handleDelete = async (id) => {
        if (confirm("Deseja realmente excluir este campo?")) {
            await deleteExameCampo(id);
            fetchData();
        }
    };

    return (
        <div className="container">
            <h2>Exame Campos</h2>
            <table className="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nome</th>
                        <th>Tipo</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {exameCampos.map(c => (
                        <tr key={c.id}>
                            <td>{c.id}</td>
                            <td>{c.nome}</td>
                            <td>{c.tipo}</td>
                            <td>
                                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(c.id)}>Excluir</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
