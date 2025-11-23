import { useEffect, useState } from 'react';
import { getPacientes, createPaciente, deletePaciente } from '../services/api';

export default function Pacientes() {
    const [pacientes, setPacientes] = useState([]);
    const [nome, setNome] = useState("");

    useEffect(() => { loadPacientes(); }, []);

    const loadPacientes = async () => {
        const data = await getPacientes();
        setPacientes(data);
    };

    const handleCreate = async () => {
        if (!nome) return;
        await createPaciente({ nome, activo: true });
        setNome("");
        loadPacientes();
    };

    const handleDelete = async (id) => {
        await deletePaciente(id);
        loadPacientes();
    };

    return (
        <div className="container">
            <h2>Pacientes</h2>
            <input value={nome} onChange={e => setNome(e.target.value)} placeholder="Nome do paciente" />
            <button onClick={handleCreate}>Adicionar</button>
            <table className="table table-striped mt-2">
                <thead>
                    <tr><th>ID</th><th>Nome</th><th>Ativo</th><th>Ações</th></tr>
                </thead>
                <tbody>
                    {pacientes.map(p => (
                        <tr key={p.id}>
                            <td>{p.id}</td>
                            <td>{p.nome}</td>
                            <td>{p.activo ? "Sim" : "Não"}</td>
                            <td>
                                <button onClick={() => handleDelete(p.id)}>Excluir</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
