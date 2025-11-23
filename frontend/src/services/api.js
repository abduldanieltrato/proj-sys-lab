import axios from 'axios';
const API_URL = "http://localhost:8000/api";

// ----------------- PACIENTES -----------------
export const getPacientes = async () => axios.get(`${API_URL}/pacientes/`).then(res => res.data);
export const createPaciente = async (data) => axios.post(`${API_URL}/pacientes/`, data).then(res => res.data);
export const updatePaciente = async (id, data) => axios.put(`${API_URL}/pacientes/${id}/`, data).then(res => res.data);
export const deletePaciente = async (id) => axios.delete(`${API_URL}/pacientes/${id}/`);
export const gerarPdfPaciente = async (id) => {
    const res = await axios.get(`${API_URL}/requisicoes/${id}/pdf/`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `requisicao_${id}.pdf`);
    document.body.appendChild(link);
    link.click();
};

// ----------------- EXAMES -----------------
export const getExames = async () => axios.get(`${API_URL}/exames/`).then(res => res.data);
export const createExame = async (data) => axios.post(`${API_URL}/exames/`, data).then(res => res.data);
export const updateExame = async (id, data) => axios.put(`${API_URL}/exames/${id}/`, data).then(res => res.data);
export const deleteExame = async (id) => axios.delete(`${API_URL}/exames/${id}/`);

// ----------------- EXAME CAMPOS -----------------
export const getExameCampos = async () => axios.get(`${API_URL}/examecampos/`).then(res => res.data);
export const createExameCampo = async (data) => axios.post(`${API_URL}/examecampos/`, data).then(res => res.data);
export const updateExameCampo = async (id, data) => axios.put(`${API_URL}/examecampos/${id}/`, data).then(res => res.data);
export const deleteExameCampo = async (id) => axios.delete(`${API_URL}/examecampos/${id}/`);

// ----------------- REQUISIÇÕES -----------------
export const getRequisicoes = async () => axios.get(`${API_URL}/requisicoes/`).then(res => res.data);
export const createRequisicao = async (data) => axios.post(`${API_URL}/requisicoes/`, data).then(res => res.data);
export const updateRequisicao = async (id, data) => axios.put(`${API_URL}/requisicoes/${id}/`, data).then(res => res.data);
export const deleteRequisicao = async (id) => axios.delete(`${API_URL}/requisicoes/${id}/`);
export const gerarPdfRequisicao = async (id) => {
    const res = await axios.get(`${API_URL}/requisicoes/${id}/pdf/`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `requisicao_${id}.pdf`);
    document.body.appendChild(link);
    link.click();
};

// ----------------- RESULTADOS -----------------
export const getResultados = async () => axios.get(`${API_URL}/resultados/`).then(res => res.data);
export const createResultado = async (data) => axios.post(`${API_URL}/resultados/`, data).then(res => res.data);
export const updateResultado = async (id, data) => axios.put(`${API_URL}/resultados/${id}/`, data).then(res => res.data);
export const deleteResultado = async (id) => axios.delete(`${API_URL}/resultados/${id}/`);
export const gerarPdfResultado = async (id) => {
    const res = await axios.get(`${API_URL}/resultados/${id}/pdf/`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `resultado_${id}.pdf`);
    document.body.appendChild(link);
    link.click();
};
