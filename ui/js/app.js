const $ = (selector) => document.querySelector(selector);

let dashboardData = null;

const pageNames = {
    dashboard: "Painel",
    diagnostics: "Diagnóstico",
    spotify: "Spotify",
    settings: "Configurações"
};

function showToast(message) {
    const toast = $("#toast");
    toast.textContent = message;
    toast.classList.add("visible");

    window.setTimeout(() => {
        toast.classList.remove("visible");
    }, 2600);
}

function navigateTo(page) {
    if (!pageNames[page]) return;

    document.querySelectorAll(".page").forEach((element) => {
        element.classList.toggle("active", element.id === `page-${page}`);
    });

    document.querySelectorAll(".nav-item").forEach((element) => {
        element.classList.toggle("active", element.dataset.page === page);
    });

    $("#current-section").textContent = pageNames[page];
    $("#page-heading").textContent =
        page === "dashboard" ? "Centro de controle" : pageNames[page];

    if (page === "diagnostics" && dashboardData) {
        renderDiagnostics(dashboardData.diagnostics);
    }
}

function renderLogs(logs) {
    const container = $("#log-list");
    container.replaceChildren();

    if (!logs || logs.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty-state";
        empty.textContent = "Nenhuma atividade registrada.";
        container.appendChild(empty);
        return;
    }

    [...logs].reverse().forEach((entry) => {
        const row = document.createElement("div");
        row.className = "log-entry";

        const time = document.createElement("span");
        time.className = "log-time";
        time.textContent = entry.time;

        const level = document.createElement("span");
        level.className = "log-level";
        level.textContent = entry.level;

        const message = document.createElement("span");
        message.className = "log-message";
        message.textContent = entry.message;

        row.append(time, level, message);
        container.appendChild(row);
    });
}

function renderDiagnostics(data) {
    const container = $("#diagnostic-list");
    container.replaceChildren();

    const rows = [
        ["Sistema operacional", data.operating_system],
        ["Versão do Windows", data.windows_version],
        ["Versão do Python", data.python_version],
        ["Arquitetura", data.architecture],
        ["Espaço livre", data.disk_free_gb === null ? "Indisponível" : `${data.disk_free_gb} GB`],
        ["Executável Python", data.python_executable],
        ["Modo de diagnóstico", "Somente leitura"]
    ];

    rows.forEach(([label, value]) => {
        const row = document.createElement("div");
        row.className = "diagnostic-row";

        const name = document.createElement("span");
        name.textContent = label;

        const result = document.createElement("strong");
        result.textContent = value ?? "Indisponível";

        row.append(name, result);
        container.appendChild(row);
    });
}

function applyTheme(theme) {
    document.body.dataset.theme = theme;

    document.querySelectorAll(".theme-option").forEach((button) => {
        button.classList.toggle("selected", button.dataset.theme === theme);
    });
}

async function refreshDashboard() {
    try {
        const data = await window.pywebview.api.get_dashboard_data();
        renderDashboard(data);
    } catch (error) {
        console.error("Erro ao carregar o painel:", error);
        showToast("Não foi possível carregar os dados do painel.");
    }
}

function renderDashboard(data) {
    dashboardData = data;

    $("#app-version").textContent = data.version;

    const diagnostics = data.diagnostics;

    $("#os-name").textContent = diagnostics.operating_system;
    $("#architecture").textContent = diagnostics.architecture;
    $("#disk-space").textContent =
        diagnostics.disk_free_gb === null
            ? "Indisponível"
            : `${diagnostics.disk_free_gb} GB`;

    applyTheme(data.settings.theme);
    renderLogs(data.logs);
    renderDiagnostics(diagnostics);
}


async function changeTheme(theme) {
    try {
        // Aplica a cor imediatamente na interface.
        applyTheme(theme);

        const result = await window.pywebview.api.set_theme(theme);

        if (!result.success) {
            showToast(result.message);
            return;
        }

        showToast("Tema atualizado com sucesso.");

        // Atualiza somente os registros, sem recarregar diagnósticos.
        const data = await window.pywebview.api.get_dashboard_data();

        dashboardData = data;
        renderLogs(data.logs);

    } catch (error) {
        console.error("Erro ao alterar tema:", error);
        showToast("Erro ao salvar o tema.");
    }
}

async function clearLog() {
    try {
        const result = await window.pywebview.api.clear_log();

        if (result.success) {
            await refreshDashboard();
            showToast("Registro da sessão limpo.");
        }
    } catch (error) {
        console.error(error);
        showToast("Não foi possível limpar o registro.");
    }
}

async function refreshDiagnostics() {
    try {
        const data = await window.pywebview.api.refresh_diagnostics();

        if (dashboardData) {
            dashboardData.diagnostics = data;
            renderDashboard(dashboardData);
        }

        renderDiagnostics(data);
        showToast("Diagnóstico atualizado.");
    } catch (error) {
        console.error(error);
        showToast("Falha ao atualizar diagnóstico.");
    }
}

function updateClock() {
    $("#clock").textContent = new Date().toLocaleTimeString("pt-BR", {
        hour12: false
    });
}

document.querySelectorAll("[data-page]").forEach((button) => {
    button.addEventListener("click", () => {
        navigateTo(button.dataset.page);
    });
});

document.querySelectorAll(".theme-option[data-theme]").forEach((button) => {
    button.addEventListener("click", () => {
        changeTheme(button.dataset.theme);
    });
});

$("#clear-log").addEventListener("click", clearLog);
$("#refresh-button").addEventListener("click", refreshDiagnostics);

updateClock();
window.setInterval(updateClock, 1000);

window.addEventListener("pywebviewready", refreshDashboard);


// =========================================
// NEXUS - INTEGRAÇÃO SPOTIFY
// =========================================

function setSpotifyValue(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}

function renderSpotifyStatus(status) {
    setSpotifyValue(
        "spotify-installed",
        status.spotify_installed ? "Instalado" : "Não encontrado"
    );

    setSpotifyValue(
        "spotify-running",
        status.spotify_running ? "Em execução" : "Fechado"
    );

    setSpotifyValue(
        "spotify-spicetify",
        status.spicetify_installed ? "Instalado" : "Não encontrado"
    );

    setSpotifyValue(
        "spotify-marketplace",
        status.marketplace_configured ? "Configurado" : "Não configurado"
    );

    setSpotifyValue("spotify-version", status.spicetify_version);

    setSpotifyValue(
        "spotify-feedback",
        "Diagnóstico atualizado."
    );
}

async function refreshSpotifyStatus() {
    setSpotifyValue("spotify-feedback", "Verificando Spotify...");

    try {
        const status = await window.pywebview.api.get_spotify_status();
        renderSpotifyStatus(status);
    } catch (error) {
        console.error(error);
        setSpotifyValue(
            "spotify-feedback",
            "Não foi possível consultar o Spotify."
        );
    }
}

async function launchSpotify() {
    try {
        const result = await window.pywebview.api.launch_spotify();

        setSpotifyValue("spotify-feedback", result.message);

        if (result.success) {
            showToast("Solicitação de abertura enviada.");
        } else {
            showToast("Não foi possível abrir o Spotify.");
        }
    } catch (error) {
        console.error(error);
        setSpotifyValue(
            "spotify-feedback",
            "Erro ao tentar abrir o Spotify."
        );
    }
}

document.getElementById("spotify-refresh")
    ?.addEventListener("click", refreshSpotifyStatus);

document.getElementById("spotify-launch")
    ?.addEventListener("click", launchSpotify);

window.addEventListener("pywebviewready", refreshSpotifyStatus);
