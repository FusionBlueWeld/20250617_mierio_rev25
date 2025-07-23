document.addEventListener('DOMContentLoaded', () => {
    window.currentLoadedModelFile = null;

    UIHandlers.initTabSwitching();
    UIHandlers.initLedButtons();

    ViewTab.init();
    ModelTab.init();

    UIHandlers.setupAssetFolderInput(
        'asset-folder-input',
        'asset-folder-name',
        (featureHeaders, targetHeaders) => {
            ViewTab.setFeatureHeaders(featureHeaders);
            ViewTab.setCurrentFeatureSelections({});
            ViewTab.populateFeatureParameters(featureHeaders);

            ViewTab.setTargetHeaders(targetHeaders);
            ViewTab.setCurrentTargetSelection('');
            ViewTab.populateTargetParameters(targetHeaders);

            ModelTab.setModelFittingSelections({});
            ModelTab.populateFittingTable();
            
            ViewTab.updatePlotDisplayState();
            ViewTab.updatePlot();
            UIHandlers.updateViewActionButtons(document.getElementById('overlap-toggle').checked, ModelTab.getModelConfigLoaded());
            UIHandlers.updateModelFileButtonState();
            
            console.log("Asset folder loaded and UI updated.");
        },
        () => {
            ViewTab.setFeatureHeaders([]);
            ViewTab.setCurrentFeatureSelections({});
            document.getElementById('feature-params-container').innerHTML = '';

            ViewTab.setTargetHeaders([]);
            ViewTab.setCurrentTargetSelection('');
            document.getElementById('target-params-container').innerHTML = '';

            ModelTab.setModelFittingSelections({});
            ModelTab.populateFittingTable();

            ViewTab.updatePlotDisplayState();
            ViewTab.updatePlot();
            UIHandlers.updateViewActionButtons(document.getElementById('overlap-toggle').checked, ModelTab.getModelConfigLoaded());
            UIHandlers.updateModelFileButtonState();

            console.log("Asset selection cleared and UI reset.");
        }
    );

    const modelFileInput = document.getElementById('model-file-input');
    const modelFileNameDisplay = document.getElementById('model-file-name');
    const modelDisplayName = document.getElementById('model-display-name');

    modelFileInput.addEventListener('change', async (event) => {
        if (event.target.files.length > 0) {
            const file = event.target.files[0];
            modelFileNameDisplay.value = file.name;
            
            try {
                const result = await APIService.loadModelConfig(file.name);

                if (result.error) {
                    alert(`モデル設定のロードに失敗しました: ${result.error}`);
                    modelFileNameDisplay.value = '';
                    modelDisplayName.value = '';
                    ModelTab.setModelConfigLoaded(false);
                    window.currentLoadedModelFile = null;
                } else {
                    alert(result.message);
                    ModelTab.setModelFittingSelections(result.fitting_config || {});
                    document.getElementById('fitting-method-toggle').checked = (result.fitting_method === '線形結合');
                    document.getElementById('fitting-method-label').textContent = result.fitting_method;
                    ModelTab.setModelFunctions(result.functions || []);
                    ModelTab.setModelConfigLoaded(true);

                    modelDisplayName.value = result.model_name || '';

                    window.currentLoadedModelFile = file.name;

                    ModelTab.populateFunctionTable();
                    ModelTab.populateFittingTable();
                    UIHandlers.updateViewActionButtons(document.getElementById('overlap-toggle').checked, ModelTab.getModelConfigLoaded());
                    ViewTab.updatePlot();
                }
            } catch (error) {
                console.error('Error loading model config from main screen:', error);
                alert(`モデル設定ロード中にエラーが発生しました: ${error.message}`);
                modelFileNameDisplay.value = '';
                modelDisplayName.value = '';
                ModelTab.setModelConfigLoaded(false);
                window.currentLoadedModelFile = null;
            }
        } else {
            modelFileNameDisplay.value = '';
            modelDisplayName.value = '';
            ModelTab.setModelConfigLoaded(false);
            ModelTab.resetModelSettings();
            window.currentLoadedModelFile = null;
        }
    });

    UIHandlers.updateViewActionButtons(document.getElementById('overlap-toggle').checked, ModelTab.getModelConfigLoaded());
    UIHandlers.updateModelFileButtonState();
});

document.addEventListener('DOMContentLoaded', function() {
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const sideMenu = document.getElementById('side-menu');
    const mainContentWrapper = document.getElementById('main-content-wrapper');
    const header = document.querySelector('.global-header');

    if (hamburgerBtn && sideMenu && mainContentWrapper && header) {
        hamburgerBtn.addEventListener('click', () => {
            sideMenu.classList.toggle('open');
            mainContentWrapper.classList.toggle('shifted');
            header.classList.toggle('shifted');
        });
    }
});
