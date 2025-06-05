# Especificações Técnicas de Implementação - Bubble

**Documento Técnico Detalhado**  
**Projeto:** BestStag Portal Web  
**Solicitação:** BSFT-001  
**Plataforma:** Bubble  
**Data:** 01/06/2025  
**Autor:** Agente Bubble/Softr

## Configuração Inicial do Ambiente Bubble

### Setup do Aplicativo

A criação do aplicativo BestStag no Bubble seguirá configurações otimizadas para performance, segurança e escalabilidade. O aplicativo será configurado com nome "BestStag Portal", utilizando template em branco para máximo controle sobre a implementação.

As configurações gerais incluirão definição de fuso horário padrão (UTC), idioma principal (Português Brasileiro), e configurações de SEO básicas com meta tags apropriadas. O aplicativo será configurado para suportar múltiplos idiomas, preparando para expansão internacional futura.

Configurações de domínio incluirão setup para subdomínio personalizado (portal.beststag.com) com certificado SSL automático. As configurações de email utilizarão domínio personalizado para comunicações oficiais, melhorando a credibilidade e deliverability.

### Configuração de Dados

#### Estrutura de Data Types

**User (Usuário)**
- Email (text, unique): Endereço de email único do usuário
- Password (text): Hash da senha (quando aplicável)
- First Name (text): Primeiro nome do usuário
- Last Name (text): Sobrenome do usuário
- Profile Picture (image): Foto de perfil do usuário
- Phone Number (text): Número de telefone para WhatsApp
- Company (text): Empresa onde trabalha
- Job Title (text): Cargo profissional
- Timezone (text): Fuso horário preferido
- Language (text): Idioma preferido
- Created Date (date): Data de criação da conta
- Last Login (date): Data do último login
- Account Status (text): Status da conta (active, suspended, deleted)
- Onboarding Completed (yes/no): Se completou o onboarding
- Email Verified (yes/no): Se o email foi verificado
- Two Factor Enabled (yes/no): Se 2FA está habilitado

**OAuth Integration (Integração OAuth)**
- User (User): Referência ao usuário
- Provider (text): Provedor OAuth (Google, Microsoft)
- Provider User ID (text): ID do usuário no provedor
- Access Token (text): Token de acesso (criptografado)
- Refresh Token (text): Token de renovação (criptografado)
- Token Expires At (date): Data de expiração do token
- Scopes (text): Escopos autorizados
- Created Date (date): Data da integração
- Last Sync (date): Última sincronização
- Status (text): Status da integração (active, expired, revoked)

**User Session (Sessão do Usuário)**
- User (User): Referência ao usuário
- Session Token (text): Token único da sessão
- IP Address (text): Endereço IP da sessão
- User Agent (text): Informações do navegador
- Created Date (date): Data de criação da sessão
- Last Activity (date): Última atividade
- Expires At (date): Data de expiração
- Status (text): Status da sessão (active, expired, invalidated)
- Login Method (text): Método de login utilizado

**Audit Log (Log de Auditoria)**
- User (User): Referência ao usuário (opcional)
- Event Type (text): Tipo de evento
- Description (text): Descrição detalhada
- IP Address (text): Endereço IP
- User Agent (text): Informações do navegador
- Timestamp (date): Data e hora do evento
- Additional Data (text): Dados adicionais em JSON
- Result (text): Resultado da operação

**User Preferences (Preferências do Usuário)**
- User (User): Referência ao usuário
- Notification Email (yes/no): Receber notificações por email
- Notification WhatsApp (yes/no): Receber notificações via WhatsApp
- Dashboard Layout (text): Layout preferido do dashboard
- Theme (text): Tema visual preferido
- Working Hours Start (text): Horário de início do trabalho
- Working Hours End (text): Horário de fim do trabalho
- Working Days (text): Dias de trabalho (JSON array)

#### Privacy Rules

**User Data Protection**
- Regra 1: Usuários só podem ver e modificar seus próprios dados
- Regra 2: Dados sensíveis (tokens, senhas) nunca são expostos no frontend
- Regra 3: Logs de auditoria são visíveis apenas para administradores
- Regra 4: Sessões são visíveis apenas para o usuário proprietário

**OAuth Integration Protection**
- Regra 1: Tokens OAuth nunca são expostos no frontend
- Regra 2: Apenas o usuário proprietário pode ver suas integrações
- Regra 3: Administradores podem ver status mas não tokens

### Configuração de API Connector

#### Google OAuth Configuration

**API Name:** Google OAuth  
**Authentication:** OAuth2 User-Agent Flow  

**Authorization URL:** https://accounts.google.com/o/oauth2/v2/auth  
**Access Token URL:** https://oauth2.googleapis.com/token  
**Client ID:** [Configurado via Google Cloud Console]  
**Client Secret:** [Configurado via Google Cloud Console]  

**Scopes:**
- openid
- email
- profile
- https://www.googleapis.com/auth/calendar.readonly
- https://www.googleapis.com/auth/gmail.readonly

**User Profile Call:**
- URL: https://www.googleapis.com/oauth2/v2/userinfo
- Method: GET
- Headers: Authorization: Bearer [access_token]

**User ID Path:** id  
**User Email Path:** email  

#### Microsoft OAuth Configuration

**API Name:** Microsoft OAuth  
**Authentication:** OAuth2 User-Agent Flow  

**Authorization URL:** https://login.microsoftonline.com/common/oauth2/v2.0/authorize  
**Access Token URL:** https://login.microsoftonline.com/common/oauth2/v2.0/token  
**Client ID:** [Configurado via Azure AD]  
**Client Secret:** [Configurado via Azure AD]  

**Scopes:**
- openid
- email
- profile
- offline_access
- https://graph.microsoft.com/User.Read
- https://graph.microsoft.com/Calendars.Read
- https://graph.microsoft.com/Mail.Read

**User Profile Call:**
- URL: https://graph.microsoft.com/v1.0/me
- Method: GET
- Headers: Authorization: Bearer [access_token]

**User ID Path:** id  
**User Email Path:** mail  

#### Airtable Integration

**API Name:** Airtable API  
**Authentication:** Private Key in Header  

**Base URL:** https://api.airtable.com/v0/[BASE_ID]  
**Headers:**
- Authorization: Bearer [API_KEY]
- Content-Type: application/json

**Endpoints Configurados:**
- GET /Users: Listar usuários
- POST /Users: Criar usuário
- PATCH /Users/[ID]: Atualizar usuário
- GET /Tasks: Listar tarefas
- POST /Tasks: Criar tarefa
- PATCH /Tasks/[ID]: Atualizar tarefa

## Implementação de Workflows

### Authentication Workflows

#### Workflow: User Login (Email/Password)

**Trigger:** Button "Login" is clicked  
**Conditions:** Input Email is not empty AND Input Password is not empty  

**Actions:**
1. **Log to server:** Event Type = "login_attempt", User = Input Email
2. **Only when:** User with email = Input Email exists
   - **Log in the user:** User = Search for Users (Email = Input Email)
   - **Only when:** Login successful
     - **Create a new thing:** User Session
       - User = Current User
       - Session Token = Generate random string (32 characters)
       - IP Address = Current User's IP
       - User Agent = Current User's User Agent
       - Created Date = Current date/time
       - Expires At = Current date/time + 24 hours
       - Status = "active"
       - Login Method = "email_password"
     - **Update User:** Last Login = Current date/time
     - **Log to server:** Event Type = "login_success", User = Current User
     - **Navigate to:** Dashboard
   - **Only when:** Login failed
     - **Log to server:** Event Type = "login_failed", Description = "Invalid credentials"
     - **Show alert:** "Email ou senha incorretos"

#### Workflow: OAuth Login (Google)

**Trigger:** Button "Login with Google" is clicked  

**Actions:**
1. **Log to server:** Event Type = "oauth_login_attempt", Description = "Google OAuth"
2. **Signup/login with a social network:** Google OAuth
3. **Only when:** OAuth login successful
   - **Create or Update OAuth Integration:**
     - User = Current User
     - Provider = "Google"
     - Provider User ID = OAuth response's user ID
     - Access Token = OAuth response's access token (encrypted)
     - Refresh Token = OAuth response's refresh token (encrypted)
     - Token Expires At = Calculate from expires_in
     - Scopes = OAuth response's scope
     - Status = "active"
   - **Create User Session:** (same as email login)
   - **Only when:** Current User's Onboarding Completed is "no"
     - **Navigate to:** Onboarding Step 1
   - **Only when:** Current User's Onboarding Completed is "yes"
     - **Navigate to:** Dashboard

#### Workflow: Password Reset Request

**Trigger:** Button "Reset Password" is clicked  
**Conditions:** Input Email is not empty  

**Actions:**
1. **Log to server:** Event Type = "password_reset_request", Description = Input Email
2. **Only when:** User with email = Input Email exists
   - **Create a new thing:** Password Reset Token
     - User = Search for Users (Email = Input Email)
     - Token = Generate random string (64 characters)
     - Expires At = Current date/time + 1 hour
     - Used = "no"
   - **Send email:** 
     - To: Input Email
     - Subject: "Redefinição de senha - BestStag"
     - Body: Template with reset link including token
3. **Show alert:** "Se o email existir, você receberá instruções para redefinir sua senha"

#### Workflow: Password Reset Completion

**Trigger:** Button "Update Password" is clicked (on reset page)  
**Conditions:** Input New Password is not empty AND Input Confirm Password = Input New Password  

**Actions:**
1. **Only when:** Password Reset Token exists AND Token is not expired AND Used = "no"
   - **Update User:** Password = Input New Password
   - **Update Password Reset Token:** Used = "yes"
   - **Make changes to list of things:** User Sessions (User = Current User, Status = "active")
     - Status = "invalidated"
   - **Log to server:** Event Type = "password_reset_completed", User = Token's User
   - **Navigate to:** Login page
   - **Show alert:** "Senha redefinida com sucesso"
2. **Only when:** Token is invalid or expired
   - **Show alert:** "Link de redefinição inválido ou expirado"

### Onboarding Workflows

#### Workflow: Onboarding Step 1 - Welcome

**Trigger:** Page is loaded  

**Actions:**
1. **Log to server:** Event Type = "onboarding_step_1_viewed", User = Current User
2. **Set state:** Current Step = 1

**Button "Next" Actions:**
1. **Update User:** 
   - Company = Input Company
   - Job Title = Input Job Title
2. **Navigate to:** Onboarding Step 2

#### Workflow: Onboarding Step 2 - Integrations

**Trigger:** Page is loaded  

**Actions:**
1. **Log to server:** Event Type = "onboarding_step_2_viewed", User = Current User
2. **Display:** Available integrations (Google, Microsoft)

**Button "Connect Google" Actions:**
1. **Signup/login with a social network:** Google OAuth (additional scopes)
2. **Only when:** Successful
   - **Update OAuth Integration:** (same as login workflow)
   - **Set state:** Google Connected = "yes"

**Button "Connect Microsoft" Actions:**
1. **Signup/login with a social network:** Microsoft OAuth
2. **Only when:** Successful
   - **Update OAuth Integration:** (same as login workflow)
   - **Set state:** Microsoft Connected = "yes"

#### Workflow: Onboarding Step 3 - Preferences

**Trigger:** Page is loaded  

**Actions:**
1. **Log to server:** Event Type = "onboarding_step_3_viewed", User = Current User

**Button "Save Preferences" Actions:**
1. **Create or Update User Preferences:**
   - User = Current User
   - Notification Email = Checkbox Email state
   - Notification WhatsApp = Checkbox WhatsApp state
   - Working Hours Start = Dropdown Start time
   - Working Hours End = Dropdown End time
   - Working Days = Checkbox group state (as JSON)
2. **Navigate to:** Onboarding Step 4

#### Workflow: Onboarding Step 4 - Tutorial

**Trigger:** Page is loaded  

**Actions:**
1. **Log to server:** Event Type = "onboarding_step_4_viewed", User = Current User
2. **Start tutorial sequence:** Interactive tutorial

**Button "Complete Tutorial" Actions:**
1. **Set state:** Tutorial Progress = 100%
2. **Navigate to:** Onboarding Step 5

#### Workflow: Onboarding Step 5 - WhatsApp Setup

**Trigger:** Page is loaded  

**Actions:**
1. **Log to server:** Event Type = "onboarding_step_5_viewed", User = Current User
2. **Generate WhatsApp activation code:** Unique code for user
3. **Display:** WhatsApp number and activation instructions

**Button "Test Connection" Actions:**
1. **API Call:** Send test message via WhatsApp API
2. **Only when:** Successful
   - **Set state:** WhatsApp Connected = "yes"
   - **Show alert:** "Conexão com WhatsApp estabelecida!"

**Button "Complete Onboarding" Actions:**
1. **Update User:** Onboarding Completed = "yes"
2. **Log to server:** Event Type = "onboarding_completed", User = Current User
3. **Navigate to:** Dashboard

### Security Workflows

#### Workflow: Session Validation

**Trigger:** Page is loaded (on all protected pages)  

**Actions:**
1. **Only when:** Current User is logged in
   - **Only when:** Current User's session exists AND session is not expired
     - **Update User Session:** Last Activity = Current date/time
   - **Only when:** Current User's session is expired OR doesn't exist
     - **Log out the user**
     - **Navigate to:** Login page
2. **Only when:** Current User is not logged in
   - **Navigate to:** Login page

#### Workflow: Suspicious Activity Detection

**Trigger:** User login successful  

**Actions:**
1. **Only when:** Current User's IP is different from last login AND location is significantly different
   - **Send email:** Security alert to user
   - **Log to server:** Event Type = "suspicious_login", Additional Data = IP and location info
   - **Create notification:** Security alert in user's dashboard

#### Workflow: Session Cleanup

**Trigger:** Scheduled workflow (runs every hour)  

**Actions:**
1. **Make changes to list of things:** User Sessions (Expires At < Current date/time, Status = "active")
   - Status = "expired"
2. **Delete list of things:** User Sessions (Status = "expired", Created Date < Current date/time - 30 days)

## Implementação de Interface

### Páginas Principais

#### Login Page

**Elements:**
- **Group Login Container:** Centered container with max-width 400px
  - **Image Logo:** BestStag logo, centered
  - **Input Email:** Type = email, placeholder = "Seu email"
  - **Input Password:** Type = password, placeholder = "Sua senha"
  - **Button Login:** Text = "Entrar", full width
  - **Text Divider:** "ou"
  - **Button Google Login:** Text = "Entrar com Google", Google colors
  - **Button Microsoft Login:** Text = "Entrar com Microsoft", Microsoft colors
  - **Link Forgot Password:** Text = "Esqueci minha senha"
  - **Link Sign Up:** Text = "Criar conta"

**Styling:**
- Background: Linear gradient (#667eea to #764ba2)
- Container: White background, border-radius 8px, box-shadow
- Buttons: Primary color #667eea, hover effects
- Inputs: Border-radius 4px, focus states

#### Dashboard Page

**Elements:**
- **Header:** 
  - **Group Navigation:** Horizontal menu with logo and user menu
  - **Text Welcome:** "Olá, [User's First Name]!"
  - **Group Quick Stats:** Cards with key metrics
- **Main Content:**
  - **Group Tasks Widget:** Recent and pending tasks
  - **Group Calendar Widget:** Upcoming events
  - **Group Email Widget:** Important emails summary
  - **Group Quick Actions:** Buttons for common actions

**Responsive Design:**
- Desktop: 3-column layout for widgets
- Tablet: 2-column layout
- Mobile: Single column, stacked widgets

#### Settings Page

**Elements:**
- **Group Settings Navigation:** Sidebar with categories
- **Group Profile Settings:** Personal information form
- **Group Integration Settings:** Connected services management
- **Group Notification Settings:** Notification preferences
- **Group Security Settings:** Password, 2FA, sessions

### Reusable Elements

#### User Menu (Header Element)

**Elements:**
- **Image Profile Picture:** User's photo or default avatar
- **Text User Name:** Current User's First Name + Last Name
- **Group Dropdown Menu:**
  - **Link Dashboard:** Navigate to dashboard
  - **Link Settings:** Navigate to settings
  - **Link Help:** Navigate to help
  - **Button Logout:** Logout workflow

#### Notification Toast (Reusable Element)

**Elements:**
- **Group Toast Container:** Fixed position, top-right
- **Text Message:** Dynamic notification text
- **Button Close:** Close notification
- **Icon Type:** Success, error, warning, info icons

**States:**
- **State Type:** success, error, warning, info
- **State Visible:** yes/no for show/hide animation

#### Loading Spinner (Reusable Element)

**Elements:**
- **Group Spinner Container:** Centered overlay
- **Icon Spinner:** Rotating loading icon
- **Text Loading Message:** Dynamic loading text

### Responsive Design Configuration

#### Breakpoints
- **Desktop:** 1200px and above
- **Tablet:** 768px to 1199px
- **Mobile:** 767px and below

#### Layout Rules
- **Desktop:** Full sidebar navigation, multi-column layouts
- **Tablet:** Collapsible sidebar, 2-column layouts
- **Mobile:** Bottom navigation, single-column layouts

#### Typography Scale
- **H1:** 32px desktop, 28px tablet, 24px mobile
- **H2:** 24px desktop, 22px tablet, 20px mobile
- **Body:** 16px desktop, 16px tablet, 14px mobile
- **Small:** 14px desktop, 14px tablet, 12px mobile

## Configuração de Segurança

### SSL e HTTPS

**Configuração:**
- SSL automático habilitado via Bubble
- Redirecionamento HTTP para HTTPS forçado
- HSTS headers configurados
- Certificado SSL renovação automática

### Content Security Policy

**Headers configurados:**
```
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'unsafe-inline' *.googleapis.com *.microsoft.com;
  style-src 'self' 'unsafe-inline' *.googleapis.com;
  img-src 'self' data: *.googleapis.com *.microsoft.com;
  connect-src 'self' *.googleapis.com *.microsoft.com api.airtable.com;
  frame-src 'self' *.googleapis.com *.microsoft.com;
```

### Rate Limiting

**Configurações:**
- Login attempts: 5 per minute per IP
- Password reset: 3 per hour per email
- API calls: 100 per minute per user
- Registration: 10 per hour per IP

### Data Encryption

**Sensitive Data:**
- OAuth tokens: AES-256 encryption
- Session tokens: SHA-256 hashing
- Passwords: bcrypt with salt rounds 12
- API keys: Environment variables only

### Privacy Compliance

**LGPD/GDPR Compliance:**
- Data minimization: Only collect necessary data
- Consent management: Clear opt-in for data processing
- Right to deletion: User can delete account and data
- Data portability: Export user data functionality
- Privacy policy: Clear and accessible

---

*Este documento técnico fornece todas as especificações necessárias para implementação completa do sistema de autenticação do BestStag no Bubble.*

