// ============================================================
// requisicao_analise_admin.js
// Autor: Trato
// Objetivo: Mostrar/ocultar campos de ResultadoItem dinamicamente
//           com base no exame selecionado.
// Compatível com Django Admin
// ============================================================

(function($) {
    $(document).ready(function() {

        // ==============================
        // Função principal
        // ==============================
        function atualizarCampos() {
            // Esconde todos os inlines de ResultadoItem
            $('.inline-related').hide();

            // Captura exames selecionados (checkboxes)
            var examesSelecionados = $('#id_exames input:checked').map(function() {
                return $(this).val();
            }).get();

            // Itera sobre cada inline e exibe apenas se pertencer ao exame selecionado
            $('.inline-related').each(function() {
                var $inline = $(this);
                var select = $inline.find('select[id$="exame_campo"]');

                if (select.length) {
                    var exameId = select.find('option:selected').data('exame-id');
                    if (examesSelecionados.includes(exameId?.toString())) {
                        $inline.show();
                    }
                }
            });
        }

        // ==============================
        // Inicialização
        // ==============================
        atualizarCampos();

        // ==============================
        // Eventos
        // ==============================
        $('#id_exames input[type=checkbox]').on('change', atualizarCampos);
        $('select[id$="exame_campo"]').on('change', atualizarCampos);

    });
})(django.jQuery);
