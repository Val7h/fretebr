# WEEK 3 - QUICK REFERENCE GUIDE

**Project**: FreteBR - Frontend Match & Chat Features
**Status**: ✅ COMPLETE
**Branch**: `dev`
**Date**: 2026-06-05

---

## Files Created

### Pages (5)
| File | Lines | Purpose |
|------|-------|---------|
| `frontend/src/pages/MyMatchesPage.tsx` | 277 | Match list with filters |
| `frontend/src/pages/MatchDetailPage.tsx` | 206 | Match details + timeline |
| `frontend/src/pages/ChatPage.tsx` | 223 | Chat interface |
| `frontend/src/pages/FreteDetailPage.tsx` | +35 | Updated: Add "Quero Este Frete" |
| `frontend/src/pages/DashboardPage.tsx` | +8 | Updated: Add "Meus Matches" |

### Components (2)
| File | Lines | Purpose |
|------|-------|---------|
| `frontend/src/components/MatchTimeline.tsx` | 56 | Status timeline visual |
| `frontend/src/components/ChatMessage.tsx` | 50 | Individual message display |

### Services (1)
| File | Lines | Purpose |
|------|-------|---------|
| `frontend/src/services/matchesApi.ts` | 108 | Match & message API calls |

### Documentation (3)
| File | Purpose |
|------|---------|
| `SEMANA_3_FRONTEND_COMPLETED.md` | Feature completeness |
| `WEEK_3_VERIFICATION_CHECKLIST.md` | Detailed verification |
| `SEMANA_3_FINAL_REPORT.md` | Final summary |

---

## Routes Added

```javascript
// Protected routes (all require login)
/meus-matches              → MyMatchesPage
/match/:id                 → MatchDetailPage
/match/:id/chat            → ChatPage
```

---

## Key Components

### MyMatchesPage
**Features**:
- List of user's matches in responsive grid
- Filter buttons: All, Pendentes, Aceito, Em Entrega, Finalizado
- Status badges with emojis
- Action buttons: Chat & Details
- Empty state handling

**Props**: None (uses useAuth + matchesApi)
**Navigation**: ← Dashboard, → MatchDetail/Chat

### MatchDetailPage
**Features**:
- Complete match information
- Visual timeline showing status
- Other user details
- Status-based action buttons
- Loading/error states

**Props**: `id` from URL params
**Key Hooks**: 
- `useParams()` - Get match ID
- `useNavigate()` - Navigation
- `useAuth()` - User info
- `useState()` - Loading, error
- `useEffect()` - Fetch match

### ChatPage
**Features**:
- Message list with auto-scroll
- 3-second polling for new messages
- Send new message form
- Character counter
- Loading/sending states

**Props**: None (uses match ID from URL)
**Key Hooks**:
- `useRef()` - Auto-scroll to bottom
- `useEffect()` - Polling setup
- `useState()` - Messages, input

### MatchTimeline
**Props**:
```typescript
interface MatchTimelineProps {
  currentStatus: MatchStatus
}
```

**Example**:
```jsx
<MatchTimeline currentStatus="aceito" />
```

### ChatMessage
**Props**:
```typescript
interface ChatMessageProps {
  message: Message
  isOwn: boolean
}
```

**Example**:
```jsx
<ChatMessage 
  message={message} 
  isOwn={message.sender_id === currentUser.id}
/>
```

---

## API Service Methods

### matchesApi

```typescript
// Get all matches for current user
matchesApi.getMatches(): Promise<Match[]>

// Get single match by ID
matchesApi.getMatchById(id: string): Promise<Match>

// Accept a frete (create new match)
matchesApi.acceptFrete(payload: { frete_id: string }): Promise<Match>

// Update match status (motorista only)
matchesApi.updateMatchStatus(
  id: string, 
  payload: { status: MatchStatus }
): Promise<Match>

// Get all messages for a match
matchesApi.getMessages(matchId: string): Promise<Message[]>

// Send new message to match
matchesApi.sendMessage(
  matchId: string, 
  content: string
): Promise<Message>
```

---

## Type Definitions

### Match
```typescript
interface Match {
  id: string
  frete_id: string
  shipper_id: string
  motorista_id: string
  status: 'pendente' | 'aceito' | 'em_entrega' | 'finalizado'
  created_at: string
  updated_at: string
  frete?: {
    id: string
    origem: string
    destino: string
    peso_kg: number
    valor_r: number
    descricao?: string
    motorista_id: string
  }
  shipper?: {
    id: string
    nome: string
    email: string
  }
  motorista?: {
    id: string
    nome: string
    email: string
  }
}
```

### Message
```typescript
interface Message {
  id: string
  match_id: string
  sender_id: string
  sender_nome: string
  content: string
  created_at: string
}
```

---

## Usage Examples

### Accepting a Frete
```typescript
// In FreteDetailPage
const handleAcceptFrete = async () => {
  try {
    await matchesApi.acceptFrete({ frete_id: frete.id })
    // Redirect after success
    navigate('/meus-matches')
  } catch (err) {
    setError(err.message)
  }
}
```

### Updating Match Status
```typescript
// In MatchDetailPage
const handleUpdateStatus = async (newStatus: MatchStatus) => {
  try {
    const updated = await matchesApi.updateMatchStatus(
      match.id, 
      { status: newStatus }
    )
    setMatch(updated)
  } catch (err) {
    setError(err.message)
  }
}
```

### Sending Message
```typescript
// In ChatPage
const handleSendMessage = async (e: React.FormEvent) => {
  e.preventDefault()
  try {
    await matchesApi.sendMessage(matchId, messageText)
    setMessageText('')
    // Refresh messages
    const messages = await matchesApi.getMessages(matchId)
    setMessages(messages)
  } catch (err) {
    setError(err.message)
  }
}
```

---

## Common Patterns

### Loading State
```typescript
const [isLoading, setIsLoading] = useState(true)
const [error, setError] = useState('')

useEffect(() => {
  const fetch = async () => {
    try {
      setIsLoading(true)
      const data = await api.getData()
      setData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }
  fetch()
}, [])

return (
  <>
    {isLoading && <p>Loading...</p>}
    {error && <p className="text-red-700">{error}</p>}
    {data && <Component data={data} />}
  </>
)
```

### Role-Based Rendering
```typescript
const isMotoristaUser = currentUser?.tipo === 'motorista'

return (
  <>
    {isMotoristaUser && <MotoristaComponent />}
    {!isMotoristaUser && <ShipperComponent />}
  </>
)
```

### Message Polling
```typescript
useEffect(() => {
  const pollInterval = setInterval(() => {
    fetchMessages()
  }, 3000) // 3 seconds

  return () => clearInterval(pollInterval) // Cleanup
}, [])
```

---

## Styling Patterns

### Status Colors
```typescript
const getStatusColor = (status: MatchStatus) => {
  switch (status) {
    case 'pendente': return 'bg-red-50 border-red-200 text-red-800'
    case 'aceito': return 'bg-green-50 border-green-200 text-green-800'
    case 'em_entrega': return 'bg-blue-50 border-blue-200 text-blue-800'
    case 'finalizado': return 'bg-gray-50 border-gray-200 text-gray-800'
  }
}
```

### Responsive Grid
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => (
    <div key={item.id}>...</div>
  ))}
</div>
```

### Button States
```jsx
<button
  disabled={isLoading}
  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 ..."
>
  {isLoading ? 'Loading...' : 'Submit'}
</button>
```

---

## Testing Checklist

### Manual Testing
- [ ] Accept frete from FreteDetailPage
- [ ] Verify redirect to MyMatches
- [ ] Filter matches by status
- [ ] Open match details
- [ ] View timeline
- [ ] Send message in chat
- [ ] Verify auto-scroll
- [ ] Update match status
- [ ] Verify timeline updates

### Responsive Testing
- [ ] Mobile (375px): Single column grid
- [ ] Tablet (768px): Two column grid
- [ ] Desktop (1024px+): Three column grid
- [ ] Touch targets 44x44px minimum
- [ ] Text readable on all sizes

### Error Cases
- [ ] Network error → show message
- [ ] 404 not found → show error
- [ ] Unauthorized → redirect to login
- [ ] Validation error → show feedback
- [ ] Empty list → show empty state

---

## Debugging Tips

### Message Not Sending?
1. Check browser console for errors
2. Verify match ID in URL
3. Check token in localStorage
4. Verify API endpoint is accessible

### Timeline Not Updating?
1. Ensure `currentStatus` prop is correct
2. Check component re-render on status change
3. Verify match status enum values match

### Polling Not Working?
1. Check Network tab for requests every 3 seconds
2. Verify useEffect cleanup function
3. Check console for fetch errors
4. Verify API response format

### Styling Issues?
1. Check Tailwind class names
2. Verify no conflicting styles
3. Check responsive breakpoints (md:, lg:)
4. Browser DevTools → Inspect element

---

## Performance Notes

- Message polling: 3-second intervals (configurable)
- Auto-scroll: Uses useRef to avoid re-renders
- Button disabled states: Prevents double-submit
- Form validation: Checked before API call
- Cleanup: useEffect returns cleanup function

---

## Accessibility Features

- Semantic HTML (`button`, `form`, `main`, etc.)
- ARIA labels on inputs
- Color + icons (not color alone)
- Proper contrast ratios (WCAG AA)
- Keyboard navigation (Enter to send)
- Loading states visible
- Error messages clear

---

## Browser Support

- Chrome/Edge: Latest
- Firefox: Latest
- Safari: Latest
- Mobile browsers: iOS Safari, Chrome Mobile

---

## Deployment

### Production Build
```bash
npm run build  # Creates dist/ folder
```

### Bundle Size
- HTML: 0.45 kB (gzip: 0.29 kB)
- CSS: 6.31 kB (gzip: 1.67 kB)
- JS: 326.85 kB (gzip: 98.82 kB)

### Performance
- Build time: ~221ms
- No dead code
- Tree-shaking enabled
- Minified and optimized

---

## Resources

### Documentation
1. `SEMANA_3_FRONTEND_COMPLETED.md` - Full feature docs
2. `WEEK_3_VERIFICATION_CHECKLIST.md` - Verification details
3. `SEMANA_3_FINAL_REPORT.md` - Final report

### Files to Review
1. `frontend/src/App.tsx` - Route definitions
2. `frontend/src/services/matchesApi.ts` - API methods
3. `frontend/src/pages/MyMatchesPage.tsx` - Main feature
4. `frontend/src/pages/ChatPage.tsx` - Chat implementation

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Messages not loading | Check API response in Network tab |
| Redirect not working | Verify useNavigate() called correctly |
| Styling broken | Check Tailwind class names in browser DevTools |
| Token expired | Clear localStorage, login again |
| 404 on match ID | Verify match ID in URL params |
| Timestamps wrong | Check date parsing in ChatMessage.tsx |
| Auto-scroll not working | Verify ref is attached to end element |
| Button disabled always | Check isLoading/isSending state |

---

## Git Commands

### View Commits
```bash
git log --oneline -5                    # Last 5 commits
git show 1d92f02                        # View specific commit
```

### View Changes
```bash
git diff HEAD~4 HEAD                    # Changes in last 4 commits
git diff --stat HEAD~1 HEAD             # File changes summary
```

### Create Feature Branch
```bash
git checkout -b feature/my-feature      # New feature branch
git push origin feature/my-feature      # Push to remote
```

---

**Quick Start for New Developers**:
1. Read `SEMANA_3_FINAL_REPORT.md` first
2. Review `WEEK_3_VERIFICATION_CHECKLIST.md` for details
3. Run `npm run build` to verify code compiles
4. Read component source code for implementation details
5. Check `git log` for commit messages explaining changes

---

**Last Updated**: 2026-06-05
**Status**: ✅ Complete and Ready for Deployment
