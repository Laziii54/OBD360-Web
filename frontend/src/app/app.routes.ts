import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth-guard';

export const routes: Routes = [

  // Redirect
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'login'
  },

  // LOGIN
  {
    path: 'login',
    loadComponent: () =>
      import('./features/auth/login/login')
        .then(m => m.Login)
  },

  // REGISTER
  {
    path: 'register',
    loadComponent: () =>
      import('./features/auth/register/register')
        .then(m => m.Register)
  },

  // MAIN APPLICATION
  {
    path: 'app',
    canActivate: [authGuard],

    loadComponent: () =>
      import('./layout/main-layout/main-layout')
        .then(m => m.MainLayout),

    children: [

      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'dashboard'
      },

      // DASHBOARD
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./features/dashboard/dashboard/dashboard')
            .then(m => m.Dashboard)
      },

      // GARAGE
      {
        path: 'garage',
        loadComponent: () =>
          import('./features/garage/garage')
            .then(m => m.Garage)
      },

      // REMINDERS
      {
        path: 'reminders',
        loadComponent: () =>
          import('./features/reminders/reminders')
            .then(m => m.Reminders)
      },

      // BLUETOOTH
      {
        path: 'bluetooth',
        loadComponent: () =>
          import('./features/bluetooth/bluetooth')
            .then(m => m.Bluetooth)
      },

      // LIVE DATA
      {
        path: 'live-data',
        loadComponent: () =>
          import('./features/live-data/live-data')
            .then(m => m.LiveData)
      },

      // DTC SCANNER
      {
        path: 'dtc-scanner',
        loadComponent: () =>
          import('./features/dtc-scanner/dtc-scanner')
            .then(m => m.DtcScanner)
      },

      // ECU MODULES
      {
        path: 'ecu-modules',
        loadComponent: () =>
          import('./features/ecu-modules/ecu-modules')
            .then(m => m.EcuModules)
      },

      // GRAPHS
      {
        path: 'graphs',
        loadComponent: () =>
          import('./features/graphs/graphs')
            .then(m => m.Graphs)
      },

      // AI ASSISTANT
      {
        path: 'ai-assistant',
        loadComponent: () =>
          import('./features/ai-assistant/ai-assistant')
            .then(m => m.AiAssistant)
      },

      // SCAN HISTORY
      {
        path: 'scan-history',
        loadComponent: () =>
          import('./features/scan-history/scan-history')
            .then(m => m.ScanHistory)
      },

      // SETTINGS
      {
        path: 'settings',
        loadComponent: () =>
          import('./features/settings/settings')
            .then(m => m.Settings)
      }

    ]
  },

  // OLD DASHBOARD REDIRECT
  {
    path: 'dashboard',
    pathMatch: 'full',
    redirectTo: 'app/dashboard'
  },

  // UNKNOWN ROUTES
  {
    path: '**',
    redirectTo: 'login'
  }

];