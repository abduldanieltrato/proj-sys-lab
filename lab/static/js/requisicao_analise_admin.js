// ================================================
// requisicao_analise_admin.js
// Autor: Trato
// Objetivo: Mostrar/ocultar campos de ResultadoItem
// dinamicamente com base no exame selecionado.
// ================================================

(function($) {
    $(document).ready(function() {

        // Função para atualizar visibilidade de campos
        function atualizarCampos() {
            // Primeiro, esconde todos os inline de ResultadoItem
            $('.inline-related').each(function() {
                var $inline = $(this);
                $inline.hide();
            });

            // Para cada select de exame_campo, mostra apenas os que pertencem ao exame selecionado
            $('.inline-related').each(function() {
                var $inline = $(this);
                var select = $inline.find('select[id$="exame_campo"]');
                if (select.length) {
                    var exameId = select.find('option:selected').data('exame-id');
                    var exameSelecionado = $('#id_exames input:checked').map(function() { return $(this).val(); }).get();

                    if (exameSelecionado.includes(exameId.toString())) {
                        $inline.show();
                    }
                }
            });
        }

        // Chama função no carregamento da página
        atualizarCampos();

        // Chama função sempre que houver alteração na seleção de exames
        $('#id_exames input[type=checkbox]').change(function() {
            atualizarCampos();
        });

        // Também observa mudanças nos selects de exame_campo
        $('select[id$="exame_campo"]').change(function() {
            atualizarCampos();
        });

    });
})(django.jQuery);
