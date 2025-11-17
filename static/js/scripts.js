// static/js/scripts.js

// Wait for the entire HTML document to be loaded before running any script
document.addEventListener("DOMContentLoaded", () => {
  // --- Screen Elements ---
  const screens = {
    auth: document.getElementById("auth-screen"),
    db: document.getElementById("db-screen"),
    upload: document.getElementById("upload-screen"),
    chat: document.getElementById("chat-screen"),
  };

  const loadingOverlay = document.getElementById("loading-overlay");
  const loadingText = document.getElementById("loading-text");
  const errorToast = document.getElementById("error-toast");
  const errorMessage = document.getElementById("error-message");

  // --- Auth Elements ---
  const authSubmitBtn = document.getElementById("auth-submit-btn");
  const authToggleMode = document.getElementById("auth-toggle-mode");
  const authTitle = document.getElementById("auth-title");
  const authSubtitle = document.getElementById("auth-subtitle");
  const authBtnLabel = document.getElementById("auth-btn-label");
  const authEmail = document.getElementById("auth-email");
  const authPassword = document.getElementById("auth-password");
  const authError = document.getElementById("auth-error");
  let isLoginMode = true;

  // --- DB Screen Elements ---
  const logoutBtn = document.getElementById("logout-btn");
  const createDbBtn = document.getElementById("create-db-btn");
  const dbList = document.getElementById("db-list");
  const createDbModal = document.getElementById("create-db-modal");
  const cancelDbBtn = document.getElementById("cancel-db-btn");
  const confirmDbBtn = document.getElementById("confirm-db-btn");
  const newDbName = document.getElementById("new-db-name");

  // --- Upload Elements ---
  const uploadLogout = document.getElementById("upload-logout");
  const goChat = document.getElementById("go-chat");
  const backToDbScreen = document.getElementById("back-to-db-screen");
  const dropZone = document.getElementById("drop-zone");
  const fileUpload = document.getElementById("file-upload");
  const fileList = document.getElementById("file-list");
  const detectRelationshipsBtn = document.getElementById(
    "detect-relationships-btn"
  );
  const relationshipList = document.getElementById("relationship-list");

  // --- Chat Elements ---
  let chatThread = document.getElementById("chat-thread");
  let chatInput = document.getElementById("chat-input");
  let chatSend = document.getElementById("chat-send");

  const backToUpload = document.getElementById("back-to-upload");

  // --- Schema Elements ---
  const schemaToggle = document.getElementById("schema-toggle");
  const schemaDrawer = document.getElementById("schema-drawer");
  const schemaClose = document.getElementById("schema-close");
  const schemaContent = document.getElementById("schema-content");

  // --- Create Icons ---
  lucide.createIcons();

  // === Utility Functions ===
  function showScreen(target) {
    Object.values(screens).forEach((s) => {
      if (s) s.classList.add("hidden");
    });
    if (target) target.classList.remove("hidden");
  }
  function showLoading(show, text = "Please wait...") {
    if (loadingText) loadingText.textContent = text;
    if (loadingOverlay) loadingOverlay.classList.toggle("hidden", !show);
  }
  function showError(message, element = errorToast) {
    const msgEl = element === errorToast ? errorMessage : element;
    if (msgEl) msgEl.textContent = message;
    if (element) element.classList.remove("hidden");
    setTimeout(() => {
      if (element) element.classList.add("hidden");
    }, 3000);
  }
  function setButtonLoading(button, isLoading) {
    if (!button) return;
    if (isLoading) {
      button.disabled = true;
      button.innerHTML = '<div class="spinner"></div>';
    } else {
      button.disabled = false;
      button.innerHTML = button.dataset.originalContent;
    }
  }
  async function apiFetch(url, options = {}) {
    const response = await fetch(url, options);
    if (response.status === 401) {
      showError("Session expired. Please log in again.");
      setTimeout(() => (window.location.href = "/app"), 1000);
      return null;
    }
    return response;
  }
  [
    authSubmitBtn,
    uploadLogout,
    detectRelationshipsBtn,
    goChat,
    chatSend,
    logoutBtn,
    createDbBtn,
    confirmDbBtn,
  ].forEach((btn) => {
    if (btn) btn.dataset.originalContent = btn.innerHTML;
  });

  // === Auth Logic ===
  if (authToggleMode) {
    authToggleMode.addEventListener("click", () => {
      isLoginMode = !isLoginMode;
      authError.classList.add("hidden");
      if (isLoginMode) {
        authTitle.textContent = "Login";
        authSubtitle.textContent = "Enter your credentials.";
        authBtnLabel.textContent = "Login";
        authToggleMode.innerHTML =
          "Don’t have an account? <span class='font-medium'>Register</span>";
      } else {
        authTitle.textContent = "Create Account";
        authSubtitle.textContent = "Start your data journey.";
        authBtnLabel.textContent = "Register";
        authToggleMode.innerHTML =
          "Already have an account? <span class='font-medium'>Login</span>";
      }
    });
  }
  if (authSubmitBtn) {
    authSubmitBtn.addEventListener("click", async () => {
      const email = authEmail.value;
      const password = authPassword.value;
      if (!email || !password) {
        showError("Please enter email and password.", authError);
        return;
      }
      const endpoint = isLoginMode ? "/api/login" : "/api/register";
      setButtonLoading(authSubmitBtn, true);
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const data = await res.json();
        if (data.success) {
          if (!isLoginMode) {
            alert("Account created! Please login.");
            authToggleMode.click();
          } else {
            await loadDatabases();
          }
        } else {
          showError(data.error, authError);
        }
      } catch (e) {
        showError("Connection error.", authError);
      } finally {
        setButtonLoading(authSubmitBtn, false);
      }
    });
  }

  // === DB Selection Logic ===
  async function loadDatabases() {
    showLoading(true, "Loading databases...");
    try {
      const res = await apiFetch("/api/databases");
      if (!res) return;
      const data = await res.json();
      if (data.success) {
        showScreen(screens.db);
        dbList.innerHTML = "";
        if (data.databases.length === 0) {
          dbList.innerHTML = `<p class="text-slate-500 text-sm">No databases found. Click "New Database" to create one.</p>`;
        }
        data.databases.forEach((db) => {
          dbList.innerHTML += `
            <div class="bg-white p-5 rounded-xl border border-slate-200 hover:shadow-md transition cursor-pointer group relative db-item-btn" data-db-id="${db.id}">
              <div class="flex justify-between items-start mb-2">
                <div class="p-2 bg-sky-50 rounded-lg text-sky-600"><i data-lucide="database"></i></div>
                <div class="flex gap-1">
                  <button class="text-slate-300 hover:text-slate-700 p-1 rename-db-btn" data-db-id="${db.id}" data-db-name="${db.name}"><i data-lucide="edit-2" class="w-3 h-3"></i></button>
                  <button class="text-slate-300 hover:text-red-500 p-1 delete-db-btn" data-db-id="${db.id}" data-db-name="${db.name}"><i data-lucide="trash-2" class="w-3 h-3"></i></button>
                </div>
              </div>
              <h3 class="font-semibold text-slate-800">${db.name}</h3>
              <p class="text-xs text-slate-500">${db.table_count} tables</p>
            </div>
          `;
        });
        lucide.createIcons();
      }
    } catch (e) {
      showError("Could not load databases.");
    } finally {
      showLoading(false);
    }
  }

  if (dbList) {
    dbList.addEventListener("click", (e) => {
      const openBtn = e.target.closest(".db-item-btn");
      const renameBtn = e.target.closest(".rename-db-btn");
      const deleteBtn = e.target.closest(".delete-db-btn");

      if (renameBtn) {
        e.stopPropagation();
        const id = renameBtn.dataset.dbId;
        const name = renameBtn.dataset.dbName;
        renameDatabase(id, name);
      } else if (deleteBtn) {
        e.stopPropagation();
        const id = deleteBtn.dataset.dbId;
        const name = deleteBtn.dataset.dbName;
        deleteDatabase(id, name);
      } else if (openBtn) {
        const id = openBtn.dataset.dbId;
        openDatabase(id);
      }
    });
  }

  async function openDatabase(id) {
    showLoading(true, "Opening database...");
    try {
      const res = await apiFetch("/api/databases/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      if (!res) return;
      const data = await res.json();
      if (data.success) {
        renderSchema(data.schema);
        const schemaSize = data.schema ? Object.keys(data.schema).length : 0;
        if (goChat) goChat.disabled = schemaSize === 0;
        showScreen(screens.upload);
      } else {
        showError(data.error);
      }
    } catch (e) {
      showError("Error opening database.");
    } finally {
      showLoading(false);
    }
  }

  async function renameDatabase(id, currentName) {
    const newName = prompt("Enter a new database name:", currentName);
    if (newName && newName !== currentName) {
      const res = await apiFetch(`/api/databases/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName }),
      });
      if (!res) return;
      const data = await res.json();
      if (data.success) loadDatabases();
      else showError(data.error);
    }
  }

  async function deleteDatabase(id, name) {
    if (
      !confirm(
        `Are you sure you want to delete "${name}"?\nAll tables inside it will be lost.`
      )
    )
      return;

    const res = await apiFetch(`/api/databases/${id}`, { method: "DELETE" });
    if (!res) return;
    const data = await res.json();
    if (data.success) loadDatabases();
    else showError(data.error);
  }

  if (createDbBtn) {
    createDbBtn.addEventListener("click", () =>
      createDbModal.classList.remove("hidden")
    );
    cancelDbBtn.addEventListener("click", () =>
      createDbModal.classList.add("hidden")
    );
    confirmDbBtn.addEventListener("click", async () => {
      const name = newDbName.value;
      if (!name) return;
      setButtonLoading(confirmDbBtn, true);
      try {
        const res = await apiFetch("/api/databases", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name }),
        });
        const data = await res.json();
        if (data.success) {
          newDbName.value = "";
          createDbModal.classList.add("hidden");
          loadDatabases();
        } else {
          showError(data.error);
        }
      } catch (e) {
        showError("Could not create database.");
      } finally {
        setButtonLoading(confirmDbBtn, false);
      }
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      showLoading(true, "Logging out...");
      await apiFetch("/api/logout", { method: "POST" });
      window.location.href = "/app";
    });
  }

  // === Upload Logic ===
  if (uploadLogout) {
    uploadLogout.addEventListener("click", async () => {
      showLoading(true, "Logging out...");
      await apiFetch("/api/logout", { method: "POST" });
      window.location.href = "/app";
    });
  }
  if (backToDbScreen) {
    backToDbScreen.addEventListener("click", () => loadDatabases());
  }

  if (dropZone) {
    ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
      dropZone.addEventListener(
        eventName,
        (e) => {
          e.preventDefault();
          e.stopPropagation();
        },
        false
      );
    });
    ["dragenter", "dragover"].forEach((eventName) => {
      dropZone.addEventListener(
        eventName,
        () => dropZone.classList.add("bg-slate-100"),
        false
      );
    });
    ["dragleave", "drop"].forEach((eventName) => {
      dropZone.addEventListener(
        eventName,
        () => dropZone.classList.remove("bg-slate-100"),
        false
      );
    });
    dropZone.addEventListener("click", () => fileUpload.click());
    dropZone.addEventListener("drop", (e) => {
      fileUpload.files = e.dataTransfer.files;
      handleFiles(fileUpload.files);
    });
    fileUpload.addEventListener("change", () => {
      handleFiles(fileUpload.files);
    });
  }

  async function handleFiles(files) {
    if (files.length === 0) return;
    const formData = new FormData();
    for (const file of files) {
      if (file.type !== "text/csv" && !file.name.endsWith(".csv")) {
        showError(`File "${file.name}" is not a CSV.`);
        continue;
      }
      formData.append("files", file);
    }
    if (formData.getAll("files").length === 0) return;

    showLoading(true, "Uploading, parsing, and inferring types...");
    try {
      const response = await apiFetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      if (!response) return;
      const data = await response.json();
      if (data.success) {
        renderSchema(data.schema);
        goChat.disabled = false;
        const schemaSize = Object.keys(data.schema).length;
        detectRelationshipsBtn.disabled = schemaSize < 2;
        if (schemaSize >= 2) await detectRelationships(true);
      } else {
        showError(data.error);
      }
    } catch (error) {
      showError("File upload failed.");
    } finally {
      showLoading(false);
      fileUpload.value = null;
    }
  }

  if (fileList) {
    fileList.addEventListener("click", async (e) => {
      const renameBtn = e.target.closest(".rename-btn");
      const deleteBtn = e.target.closest(".delete-btn");

      if (renameBtn) {
        const tableId = renameBtn.dataset.tableId;
        handleRenameTable(tableId);
      }
      if (deleteBtn) {
        const tableId = deleteBtn.dataset.tableId;
        handleDeleteTable(tableId);
      }
    });
  }

  async function handleRenameTable(tableId) {
    const input = fileList.querySelector(`input[data-table-id="${tableId}"]`);
    const newName = input.value.trim();
    if (!newName) {
      showError("Table name cannot be empty.");
      return;
    }

    const res = await apiFetch(`/api/tables/${tableId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName }),
    });
    if (!res) return;
    const data = await res.json();
    if (data.success) {
      alert("Table renamed successfully!");
      updateSchemaFromServer();
    } else showError(data.error);
  }

  async function handleDeleteTable(tableId) {
    const input = fileList.querySelector(`input[data-table-id="${tableId}"]`);
    if (!confirm(`Are you sure you want to delete the table "${input.value}"?`))
      return;

    const res = await apiFetch(`/api/tables/${tableId}`, { method: "DELETE" });
    if (!res) return;
    const data = await res.json();
    if (data.success) {
      alert("Table deleted.");
      updateSchemaFromServer();
    } else showError(data.error);
  }

  async function updateSchemaFromServer() {
    try {
      const response = await apiFetch("/api/schema");
      if (!response) return;
      const data = await response.json();
      if (data.success) {
        renderSchema(data.schema);
        goChat.disabled = !data.schema || Object.keys(data.schema).length === 0;
        detectRelationshipsBtn.disabled =
          !data.schema || Object.keys(data.schema).length < 2;
      } else {
        renderSchema({});
      }
    } catch (error) {
      console.error("Error fetching schema:", error);
    }
  }

  function renderSchema(schema) {
    fileList.innerHTML = "";
    if (!schema || Object.keys(schema).length === 0) {
      fileList.innerHTML =
        '<p class="text-[11px] text-slate-400 text-center py-4">Upload files using the panel on the left.</p>';
      return;
    }

    Object.entries(schema).forEach(([tableName, details]) => {
      fileList.innerHTML += `
        <div class="flex flex-wrap items-center justify-between gap-3 border border-slate-100 rounded-2xl px-3 py-2.5 bg-slate-50">
          <div class="flex items-center gap-2">
            <i data-lucide="file-text" class="text-sky-500 w-4 h-4"></i>
            <div>
              <p class="text-slate-700 text-xs font-medium">${
                details.filename
              }</p>
              <p class="text-[11px] text-slate-400">${
                details.row_count || 0
              } rows</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <input type="text" value="${tableName}" data-table-id="${
        details.id
      }"
                   class="w-28 p-1.5 border border-slate-200 rounded-lg text-[11px] focus:ring-1 focus:ring-sky-500">
            <button data-table-id="${details.id}" data-original-content="Rename"
                    class="rename-btn text-[10px] bg-slate-200 text-slate-600 px-2 py-1 rounded-md hover:bg-slate-300">
              Rename
            </button>
            <button data-table-id="${details.id}"
                    class="delete-btn text-slate-400 hover:text-red-500 p-1">
              <i data-lucide="trash-2" class="w-3 h-3"></i>
            </button>
          </div>
        </div>
      `;
    });

    schemaContent.innerHTML = "";
    let tablesHTML = '<ul class="space-y-1">';
    let columnsHTML = '<div class="space-y-2">';

    Object.entries(schema).forEach(([tableName, details]) => {
      tablesHTML += `<li class="flex items-center justify-between"><span>${tableName}</span><span class="text-slate-400">${
        details.row_count || 0
      } rows</span></li>`;
      let colList = "";
      if (details.types) {
        Object.entries(details.types).forEach(([colName, colType]) => {
          let typeColor =
            colType === "int" || colType === "float"
              ? "text-amber-600"
              : "text-emerald-600";
          colList += `<li class="flex justify-between"><span>${colName}</span><span class="${typeColor} font-medium">${colType}</span></li>`;
        });
      }
      columnsHTML += `<div><p class="font-semibold text-slate-600 mb-1">${tableName}</p><ul class="pl-2 space-y-0.5 text-slate-500">${colList}</ul></div>`;
    });
    tablesHTML += "</ul>";
    columnsHTML += "</div>";

    schemaContent.innerHTML = `
      <div><p class="font-semibold text-slate-700 mb-1 flex items-center gap-1"><i data-lucide="table" class="w-3.5 h-3.5 text-sky-500"></i> Tables</p>${tablesHTML}</div>
      <div id="schema-relationships"></div>
      <details><summary class="font-semibold text-slate-700 mb-1 flex items-center gap-1 mt-3 cursor-pointer"><i data-lucide="columns" class="w-3.5 h-3.5 text-violet-500"></i> Columns</summary>${columnsHTML}</details>
    `;
    lucide.createIcons();
  }

  async function detectRelationships(silent = false) {
    if (!silent) setButtonLoading(detectRelationshipsBtn, true);
    relationshipList.innerHTML = "";
    try {
      const response = await apiFetch("/api/detect-relationships", {
        method: "POST",
      });
      if (!response) return;
      const data = await response.json();
      if (data.success) {
        if (data.relationships.length === 0) {
          relationshipList.innerHTML =
            '<p class="text-xs text-slate-500">No relationships detected.</p>';
        } else {
          renderRelationships(data.relationships);
        }
      } else {
        if (!silent) showError(data.error);
      }
    } catch (error) {
      if (!silent) showError("Could not detect relationships.");
    } finally {
      if (!silent) setButtonLoading(detectRelationshipsBtn, false);
    }
  }
  if (detectRelationshipsBtn)
    detectRelationshipsBtn.addEventListener("click", () =>
      detectRelationships(false)
    );

  function renderRelationships(relationships) {
    let listHTML = "";
    let schemaHTML = `<p class="font-semibold text-slate-700 mb-1 flex items-center gap-1"><i data-lucide="git-branch" class="w-3.5 h-3.5 text-emerald-500"></i> Relationships</p><ul class="space-y-1">`;
    relationships.forEach((rel) => {
      const relText = `<span class="font-semibold">${rel.from_table}.${rel.from_column}</span> → <span class="font-semibold">${rel.to_table}.${rel.to_column}</span>`;
      listHTML += `<div class="rounded-2xl border border-dashed border-emerald-200 bg-emerald-50/70 px-3 py-2.5 flex items-start gap-2"><i data-lucide="link-2" class="text-emerald-500 w-4 h-4 mt-[2px]"></i><div><p class="text-[11px] text-emerald-800 font-medium">Suggested relationship</p><p class="text-[11px] text-emerald-700">${relText}</p></div></div>`;
      schemaHTML += `<li class="text-emerald-700">${relText}</li>`;
    });
    schemaHTML += "</ul>";
    relationshipList.innerHTML = listHTML;
    const schemaRelElement = document.getElementById("schema-relationships");
    if (schemaRelElement) schemaRelElement.innerHTML = schemaHTML;
    lucide.createIcons();
  }

  // === Chat Logic ===
  if (goChat) {
    goChat.addEventListener("click", () => {
      showLoading(true, "Spinning up AI chat...");
      setTimeout(() => {
        showLoading(false);
        showScreen(screens.chat);

        chatThread = document.getElementById("chat-thread");
        chatInput = document.getElementById("chat-input");
        chatSend = document.getElementById("chat-send");

        chatSend.addEventListener("click", sendMessage);

        chatInput.addEventListener("keydown", (e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
          }
        });
      }, 700);
    });
  }

  if (backToUpload) {
    backToUpload.addEventListener("click", () => showScreen(screens.upload));
  }
  if (schemaToggle) {
    schemaToggle.addEventListener("click", () =>
      schemaDrawer.classList.toggle("-translate-x-full")
    );
    schemaClose.addEventListener("click", () =>
      schemaDrawer.classList.add("-translate-x-full")
    );
  }

  function appendBubble(html, side) {
    const wrap = document.createElement("div");
    wrap.className =
      side === "user" ? "flex justify-end" : "flex justify-start";

    const bubble = document.createElement("div");
    bubble.className =
      "max-w-[80%] px-3 py-2.5 text-xs rounded-2xl shadow-sm " +
      (side === "user" ? "bg-sky-50" : "bg-white border border-slate-100");

    bubble.innerHTML = html;

    // 🔥 This line is missing in your current file:
    wrap.appendChild(bubble);

    if (chatThread) {
      chatThread.appendChild(wrap);
      chatThread.scrollTop = chatThread.scrollHeight;
    }
  }

  function renderTable(data) {
    if (data.length === 0)
      return '<p class="text-[11px] text-slate-500">Query returned no results.</p>';
    const headers = Object.keys(data[0]);
    let table =
      '<table class="text-[11px] border border-slate-200 rounded-lg overflow-hidden w-full">';
    table += '<thead class="bg-slate-100"><tr>';
    headers.forEach((h) => (table += `<th class="p-1.5 text-left">${h}</th>`));
    table += "</tr></thead>";
    table += "<tbody>";
    data.forEach((row) => {
      table += '<tr class="hover:bg-slate-50">';
      headers.forEach(
        (h) => (table += `<td class="p-1.5 border-t">${row[h]}</td>`)
      );
      table += "</tr>";
    });
    table += "</tbody></table>";
    return `<div class="overflow-x-auto">${table}</div>`;
  }

  async function sendMessage() {
    // --- ADDED THIS CONSOLE.LOG ---
    console.log("sendMessage function called");

    const value = chatInput.value.trim();
    if (!value) return;
    appendBubble(value, "user");
    chatInput.value = "";
    setButtonLoading(chatSend, true);
    const typingEl = document.createElement("div");
    typingEl.className = "flex justify-start";
    typingEl.innerHTML = `<div class="bg-white border border-slate-100 px-3 py-2.5 text-xs rounded-2xl shadow-sm"><div class="flex gap-1 items-center"><div class="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"></div><div class="w-1.5 h-1.5 rounded-full bg-slate-300 animate-bounce [animation-delay:100ms]"></div><div class="w-1.5 h-1.5 rounded-full bg-slate-200 animate-bounce [animation-delay:200ms]"></div></div></div>`;
    chatThread.appendChild(typingEl);
    chatThread.scrollTop = chatThread.scrollHeight;
    try {
      const response = await apiFetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: value }),
      });
      if (!response) {
        chatThread.removeChild(typingEl);
        setButtonLoading(chatSend, false);
        return;
      }
      const result = await response.json();

      // --- ADDED THIS CONSOLE.LOG ---
      console.log("Received from backend:", result);

      let htmlResponse = "";
      switch (result.type) {
        case "chart":
          htmlResponse = `<p class="text-[11px] text-slate-500 mb-2">Here is the chart:</p><img src="${result.data}" alt="Generated Chart" class="rounded-lg border border-slate-200" />`;
          break;
        case "table":
          htmlResponse = `<p class="text-[11px] text-slate-500 mb-2">Here are the results:</p>${renderTable(
            result.data
          )}`;
          break;
        case "count":
          htmlResponse = `The result is: <b class="text-sky-600">${result.data}</b>`;
          break;
        case "text":
          htmlResponse = result.data;
          break;
        case "error":
          htmlResponse = `<p class="font-medium text-red-600">Error:</p><p class="text-red-500 text-[11px]">${result.data}</p>`;
          break;
      }
      if (result.query) {
        htmlResponse += `<details class="mt-2"><summary class="text-[10px] text-slate-400 cursor-pointer">Show code</summary><code class="block text-[10px] bg-slate-100 p-1.5 rounded-md mt-1">${result.query}</code></details>`;
      }
      appendBubble(htmlResponse, "ai");
    } catch (error) {
      appendBubble(
        '<p class="font-medium text-red-600">Error:</p><p class="text-red-500">Could not connect to API.</p>',
        "ai"
      );
    } finally {
      if (chatThread && typingEl.parentNode === chatThread) {
        chatThread.removeChild(typingEl);
      }
      setButtonLoading(chatSend, false);
    }
  }

  if (chatSend) chatSend.addEventListener("click", sendMessage);

  if (chatInput)
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        // <-- This was the typo, now fixed
        e.preventDefault();
        sendMessage();
      }
    });

  // === Page Load Logic ===
  async function checkAuthStatus() {
    showLoading(true, "Checking session...");
    try {
      const response = await fetch("/api/auth/status");
      const data = await response.json();
      if (data.isLoggedIn) {
        await loadDatabases(); // User is logged in, show DB screen
      } else {
        showScreen(screens.auth); // User is not logged in
      }
    } catch (error) {
      showScreen(screens.auth);
    } finally {
      showLoading(false);
    }
  }

  // Start the app
  checkAuthStatus();
}); // --- End of DOMContentLoaded wrapper
