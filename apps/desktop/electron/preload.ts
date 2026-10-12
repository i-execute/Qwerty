import { contextBridge, ipcRenderer, webUtils } from 'electron'

contextBridge.exposeInMainWorld('qwertyDesktop', {
  getConnection: profile => ipcRenderer.invoke('qwerty:connection', profile),
  revalidateConnection: () => ipcRenderer.invoke('qwerty:connection:revalidate'),
  touchBackend: profile => ipcRenderer.invoke('qwerty:backend:touch', profile),
  getGatewayWsUrl: profile => ipcRenderer.invoke('qwerty:gateway:ws-url', profile),
  openSessionWindow: (sessionId, opts) => ipcRenderer.invoke('qwerty:window:openSession', sessionId, opts),
  openWindow: () => ipcRenderer.invoke('qwerty:window:openInstance'),
  claimAmbientCue: key => ipcRenderer.invoke('qwerty:ambient:claim', key),
  petOverlay: {
    // Main renderer → main process: window lifecycle + drag. `request` is
    // `{ bounds, screen }`; resolves with the screen bounds it actually used.
    open: request => ipcRenderer.invoke('qwerty:pet-overlay:open', request),
    close: () => ipcRenderer.invoke('qwerty:pet-overlay:close'),
    setBounds: bounds => ipcRenderer.send('qwerty:pet-overlay:set-bounds', bounds),
    setIgnoreMouse: ignore => ipcRenderer.send('qwerty:pet-overlay:ignore-mouse', ignore),
    // Flip the overlay focusable (and focus it) while the composer needs keys.
    setFocusable: focusable => ipcRenderer.send('qwerty:pet-overlay:set-focusable', focusable),
    // Main renderer → overlay (forwarded by main): push the latest pet state.
    pushState: payload => ipcRenderer.send('qwerty:pet-overlay:state', payload),
    // Overlay → main renderer (forwarded by main): pop back in / composer submit.
    control: payload => ipcRenderer.send('qwerty:pet-overlay:control', payload),
    // Overlay subscribes to state pushes.
    onState: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('qwerty:pet-overlay:state', listener)

      return () => ipcRenderer.removeListener('qwerty:pet-overlay:state', listener)
    },
    // Main renderer subscribes to overlay control messages.
    onControl: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('qwerty:pet-overlay:control', listener)

      return () => ipcRenderer.removeListener('qwerty:pet-overlay:control', listener)
    }
  },
  // Quick Entry: the global-hotkey mini composer window. Main owns the OS
  // shortcut + the persisted preference; the quick window only captures text
  // and hands it back, and the primary renderer submits it through the normal
  // prompt path.
  quickEntry: {
    getSettings: () => ipcRenderer.invoke('qwerty:quick-entry:settings:get'),
    setSettings: patch => ipcRenderer.invoke('qwerty:quick-entry:settings:set', patch),
    submit: payload => ipcRenderer.send('qwerty:quick-entry:submit', payload),
    dismiss: () => ipcRenderer.send('qwerty:quick-entry:dismiss'),
    // Primary renderer → main → quick window: gateway connection state + the
    // recent-session options the target picker offers. Main caches the latest
    // payload so a freshly spawned quick window starts from truth.
    pushState: payload => ipcRenderer.send('qwerty:quick-entry:state', payload),
    // Quick window subscribes to those pushes.
    onState: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('qwerty:quick-entry:state', listener)

      return () => ipcRenderer.removeListener('qwerty:quick-entry:state', listener)
    },
    // Main → primary renderer: a submit captured by the quick window.
    onSubmit: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('qwerty:quick-entry:submit', listener)

      return () => ipcRenderer.removeListener('qwerty:quick-entry:submit', listener)
    },
    // Main → quick window: you were just summoned (reset draft + refocus).
    onShown: callback => {
      const listener = () => callback()
      ipcRenderer.on('qwerty:quick-entry:shown', listener)

      return () => ipcRenderer.removeListener('qwerty:quick-entry:shown', listener)
    }
  },
  getBootProgress: () => ipcRenderer.invoke('qwerty:boot-progress:get'),
  getConnectionConfig: profile => ipcRenderer.invoke('qwerty:connection-config:get', profile),
  saveConnectionConfig: payload => ipcRenderer.invoke('qwerty:connection-config:save', payload),
  applyConnectionConfig: payload => ipcRenderer.invoke('qwerty:connection-config:apply', payload),
  testConnectionConfig: payload => ipcRenderer.invoke('qwerty:connection-config:test', payload),
  sshConfigHosts: () => ipcRenderer.invoke('qwerty:ssh-config:hosts'),
  sshResolveHost: host => ipcRenderer.invoke('qwerty:ssh-config:resolve', host),
  probeConnectionConfig: remoteUrl => ipcRenderer.invoke('qwerty:connection-config:probe', remoteUrl),
  oauthLoginConnectionConfig: remoteUrl => ipcRenderer.invoke('qwerty:connection-config:oauth-login', remoteUrl),
  oauthLogoutConnectionConfig: remoteUrl => ipcRenderer.invoke('qwerty:connection-config:oauth-logout', remoteUrl),
  // Qwerty Cloud: one portal login powers discovery + silent per-agent sign-in
  // (cloud-auto-discovery Phase 3).
  cloud: {
    status: () => ipcRenderer.invoke('qwerty:cloud:status'),
    login: () => ipcRenderer.invoke('qwerty:cloud:login'),
    logout: () => ipcRenderer.invoke('qwerty:cloud:logout'),
    discover: org => ipcRenderer.invoke('qwerty:cloud:discover', org),
    agentSignIn: dashboardUrl => ipcRenderer.invoke('qwerty:cloud:agent-sign-in', dashboardUrl)
  },
  profile: {
    get: () => ipcRenderer.invoke('qwerty:profile:get'),
    set: name => ipcRenderer.invoke('qwerty:profile:set', name)
  },
  api: request => ipcRenderer.invoke('qwerty:api', request),
  notify: payload => ipcRenderer.invoke('qwerty:notify', payload),
  requestMicrophoneAccess: () => ipcRenderer.invoke('qwerty:requestMicrophoneAccess'),
  readFileDataUrl: filePath => ipcRenderer.invoke('qwerty:readFileDataUrl', filePath),
  readFileText: filePath => ipcRenderer.invoke('qwerty:readFileText', filePath),
  selectPaths: options => ipcRenderer.invoke('qwerty:selectPaths', options),
  writeClipboard: text => ipcRenderer.invoke('qwerty:writeClipboard', text),
  saveImageFromUrl: url => ipcRenderer.invoke('qwerty:saveImageFromUrl', url),
  saveImageBuffer: (data, ext) => ipcRenderer.invoke('qwerty:saveImageBuffer', { data, ext }),
  saveClipboardImage: () => ipcRenderer.invoke('qwerty:saveClipboardImage'),
  getPathForFile: file => {
    try {
      return webUtils.getPathForFile(file) || ''
    } catch {
      return ''
    }
  },
  normalizePreviewTarget: (target, baseDir) => ipcRenderer.invoke('qwerty:normalizePreviewTarget', target, baseDir),
  watchPreviewFile: url => ipcRenderer.invoke('qwerty:watchPreviewFile', url),
  stopPreviewFileWatch: id => ipcRenderer.invoke('qwerty:stopPreviewFileWatch', id),
  setTitleBarTheme: payload => ipcRenderer.send('qwerty:titlebar-theme', payload),
  setNativeTheme: mode => ipcRenderer.send('qwerty:native-theme', mode),
  setTranslucency: payload => ipcRenderer.send('qwerty:translucency', payload),
  setKeepAwake: on => ipcRenderer.send('qwerty:keep-awake', on),
  setPreviewShortcutActive: active => ipcRenderer.send('qwerty:previewShortcutActive', Boolean(active)),
  openExternal: url => ipcRenderer.invoke('qwerty:openExternal', url),
  openPreviewInBrowser: url => ipcRenderer.invoke('qwerty:openPreviewInBrowser', url),
  fetchLinkTitle: url => ipcRenderer.invoke('qwerty:fetchLinkTitle', url),
  sanitizeWorkspaceCwd: cwd => ipcRenderer.invoke('qwerty:workspace:sanitize', cwd),
  settings: {
    getDefaultProjectDir: () => ipcRenderer.invoke('qwerty:setting:defaultProjectDir:get'),
    setDefaultProjectDir: dir => ipcRenderer.invoke('qwerty:setting:defaultProjectDir:set', dir),
    pickDefaultProjectDir: () => ipcRenderer.invoke('qwerty:setting:defaultProjectDir:pick')
  },
  zoom: {
    // Current zoom of this window, as { level, percent }.
    get: () => ipcRenderer.invoke('qwerty:zoom:get'),
    setPercent: percent => ipcRenderer.send('qwerty:zoom:set-percent', percent),
    // Fires on every zoom change, including the Ctrl/Cmd +/-/0 shortcuts,
    // so the settings UI can stay in sync with the keyboard.
    onChanged: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('qwerty:zoom:changed', listener)

      return () => ipcRenderer.removeListener('qwerty:zoom:changed', listener)
    }
  },
  revealLogs: () => ipcRenderer.invoke('qwerty:logs:reveal'),
  getRecentLogs: () => ipcRenderer.invoke('qwerty:logs:recent'),
  readDir: dirPath => ipcRenderer.invoke('qwerty:fs:readDir', dirPath),
  gitRoot: startPath => ipcRenderer.invoke('qwerty:fs:gitRoot', startPath),
  revealPath: targetPath => ipcRenderer.invoke('qwerty:fs:reveal', targetPath),
  openDir: dirPath => ipcRenderer.invoke('qwerty:fs:openDir', dirPath),
  renamePath: (targetPath, newName) => ipcRenderer.invoke('qwerty:fs:rename', targetPath, newName),
  writeTextFile: (filePath, content) => ipcRenderer.invoke('qwerty:fs:writeText', filePath, content),
  trashPath: targetPath => ipcRenderer.invoke('qwerty:fs:trash', targetPath),
  git: {
    worktreeList: repoPath => ipcRenderer.invoke('qwerty:git:worktreeList', repoPath),
    worktreeAdd: (repoPath, options) => ipcRenderer.invoke('qwerty:git:worktreeAdd', repoPath, options),
    worktreeRemove: (repoPath, worktreePath, options) =>
      ipcRenderer.invoke('qwerty:git:worktreeRemove', repoPath, worktreePath, options),
    branchSwitch: (repoPath, branch) => ipcRenderer.invoke('qwerty:git:branchSwitch', repoPath, branch),
    branchList: repoPath => ipcRenderer.invoke('qwerty:git:branchList', repoPath),
    baseBranchList: repoPath => ipcRenderer.invoke('qwerty:git:baseBranchList', repoPath),
    repoStatus: repoPath => ipcRenderer.invoke('qwerty:git:repoStatus', repoPath),
    fileDiff: (repoPath, filePath) => ipcRenderer.invoke('qwerty:git:fileDiff', repoPath, filePath),
    scanRepos: (roots, options) => ipcRenderer.invoke('qwerty:git:scanRepos', roots, options),
    review: {
      list: (repoPath, scope, baseRef) => ipcRenderer.invoke('qwerty:git:review:list', repoPath, scope, baseRef),
      diff: (repoPath, filePath, scope, baseRef, staged) =>
        ipcRenderer.invoke('qwerty:git:review:diff', repoPath, filePath, scope, baseRef, staged),
      stage: (repoPath, filePath) => ipcRenderer.invoke('qwerty:git:review:stage', repoPath, filePath),
      unstage: (repoPath, filePath) => ipcRenderer.invoke('qwerty:git:review:unstage', repoPath, filePath),
      revert: (repoPath, filePath) => ipcRenderer.invoke('qwerty:git:review:revert', repoPath, filePath),
      revParse: (repoPath, ref) => ipcRenderer.invoke('qwerty:git:review:revParse', repoPath, ref),
      commit: (repoPath, message, push) => ipcRenderer.invoke('qwerty:git:review:commit', repoPath, message, push),
      commitContext: repoPath => ipcRenderer.invoke('qwerty:git:review:commitContext', repoPath),
      push: repoPath => ipcRenderer.invoke('qwerty:git:review:push', repoPath),
      shipInfo: repoPath => ipcRenderer.invoke('qwerty:git:review:shipInfo', repoPath),
      createPr: repoPath => ipcRenderer.invoke('qwerty:git:review:createPr', repoPath)
    }
  },
  terminal: {
    cwd: id => ipcRenderer.invoke('qwerty:terminal:cwd', id),
    dispose: id => ipcRenderer.invoke('qwerty:terminal:dispose', id),
    resize: (id, size) => ipcRenderer.invoke('qwerty:terminal:resize', id, size),
    start: options => ipcRenderer.invoke('qwerty:terminal:start', options),
    write: (id, data) => ipcRenderer.invoke('qwerty:terminal:write', id, data),
    onData: (id, callback) => {
      const channel = `qwerty:terminal:${id}:data`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)

      return () => ipcRenderer.removeListener(channel, listener)
    },
    onExit: (id, callback) => {
      const channel = `qwerty:terminal:${id}:exit`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)

      return () => ipcRenderer.removeListener(channel, listener)
    }
  },
  onClosePreviewRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('qwerty:close-preview-requested', listener)

    return () => ipcRenderer.removeListener('qwerty:close-preview-requested', listener)
  },
  onOpenUpdatesRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('qwerty:open-updates', listener)

    return () => ipcRenderer.removeListener('qwerty:open-updates', listener)
  },
  onDeepLink: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('qwerty:deep-link', listener)

    return () => ipcRenderer.removeListener('qwerty:deep-link', listener)
  },
  signalDeepLinkReady: () => ipcRenderer.invoke('qwerty:deep-link-ready'),
  onWindowStateChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('qwerty:window-state-changed', listener)

    return () => ipcRenderer.removeListener('qwerty:window-state-changed', listener)
  },
  onFocusSession: callback => {
    const listener = (_event, sessionId) => callback(sessionId)
    ipcRenderer.on('qwerty:focus-session', listener)

    return () => ipcRenderer.removeListener('qwerty:focus-session', listener)
  },
  onNotificationAction: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('qwerty:notification-action', listener)

    return () => ipcRenderer.removeListener('qwerty:notification-action', listener)
  },
  onPreviewFileChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('qwerty:preview-file-changed', listener)

    return () => ipcRenderer.removeListener('qwerty:preview-file-changed', listener)
  },
  onBackendExit: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('qwerty:backend-exit', listener)

    return () => ipcRenderer.removeListener('qwerty:backend-exit', listener)
  },
  // Soft gateway-mode apply finished tearing down the primary backend. Renderer
  // should wipe session lists + re-dial without a window reload.
  onConnectionApplied: callback => {
    const listener = () => callback()
    ipcRenderer.on('qwerty:connection:applied', listener)

    return () => ipcRenderer.removeListener('qwerty:connection:applied', listener)
  },
  onPowerResume: callback => {
    const listener = () => callback()
    ipcRenderer.on('qwerty:power-resume', listener)

    return () => ipcRenderer.removeListener('qwerty:power-resume', listener)
  },
  onBootProgress: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('qwerty:boot-progress', listener)

    return () => ipcRenderer.removeListener('qwerty:boot-progress', listener)
  },
  // First-launch bootstrap progress -- emitted by the install.ps1 stage
  // runner in main.ts (apps/desktop/electron/bootstrap-runner.ts).
  // Renderer's install overlay subscribes to live events and queries the
  // current snapshot via getBootstrapState() to recover after a devtools
  // reload mid-bootstrap.
  getBootstrapState: () => ipcRenderer.invoke('qwerty:bootstrap:get'),
  continueBootstrapLocal: () => ipcRenderer.invoke('qwerty:bootstrap:continue-local'),
  resetBootstrap: () => ipcRenderer.invoke('qwerty:bootstrap:reset'),
  repairBootstrap: () => ipcRenderer.invoke('qwerty:bootstrap:repair'),
  cancelBootstrap: () => ipcRenderer.invoke('qwerty:bootstrap:cancel'),
  onBootstrapEvent: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('qwerty:bootstrap:event', listener)

    return () => ipcRenderer.removeListener('qwerty:bootstrap:event', listener)
  },
  getVersion: () => ipcRenderer.invoke('qwerty:version'),
  getRemoteDisplayReason: () => ipcRenderer.invoke('qwerty:get-remote-display-reason'),
  uninstall: {
    summary: () => ipcRenderer.invoke('qwerty:uninstall:summary'),
    run: mode => ipcRenderer.invoke('qwerty:uninstall:run', { mode })
  },
  updates: {
    check: () => ipcRenderer.invoke('qwerty:updates:check'),
    apply: opts => ipcRenderer.invoke('qwerty:updates:apply', opts),
    getBranch: () => ipcRenderer.invoke('qwerty:updates:branch:get'),
    setBranch: name => ipcRenderer.invoke('qwerty:updates:branch:set', name),
    onProgress: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('qwerty:updates:progress', listener)

      return () => ipcRenderer.removeListener('qwerty:updates:progress', listener)
    }
  },
  themes: {
    fetchMarketplace: id => ipcRenderer.invoke('qwerty:vscode-theme:fetch', id),
    searchMarketplace: query => ipcRenderer.invoke('qwerty:vscode-theme:search', query)
  },
  // Find-in-page (Ctrl/Cmd+F): delegates to Electron's
  // webContents.findInPage on the IPC sender's window so a Cmd+F pressed
  // in a secondary session window searches THAT window, not the primary.
  // `onFoundInPage` returns the unsubscribe fn; the renderer wires it via
  // `initFindInPageListener` in store/find-in-page.ts and tears it down
  // when the FindBar unmounts.
  findInPage: (query, options) => ipcRenderer.invoke('qwerty:find-in-page', query, options),
  stopFindInPage: () => ipcRenderer.invoke('qwerty:stop-find-in-page'),
  onFoundInPage: callback => {
    const listener = (_event, result) => callback(result)
    ipcRenderer.on('qwerty:found-in-page', listener)

    return () => ipcRenderer.removeListener('qwerty:found-in-page', listener)
  }
})
