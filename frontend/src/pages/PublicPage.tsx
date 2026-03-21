import { useMutation, useQuery } from '@tanstack/react-query'
import { startTransition, useDeferredValue, useState, useRef, useEffect } from 'react'

import { ApiError, api } from '../lib/api'
import { labelName } from '../components/forms'

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  confidence?: number | string;
  matches?: { id: string; label: string; details?: string | null; kind: string }[];
  isError?: boolean;
}

const chatPrompts = [
  'Who is the Vice Chancellor?',
  'Who specializes in cloud computing?',
  'Where is Geomatic Engineering?',
]

export function PublicPage() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [directorySearch, setDirectorySearch] = useState('')
  const deferredSearch = useDeferredValue(directorySearch)
  const { data: staff = [] } = useQuery({ queryKey: ['staff'], queryFn: api.listStaff })
  const { data: departments = [] } = useQuery({ queryKey: ['departments'], queryFn: api.listDepartments })
  const { data: faculties = [] } = useQuery({ queryKey: ['faculties'], queryFn: api.listFaculties })
  const chatMutation = useMutation({ 
    mutationFn: api.queryChat,
    onMutate: (variables) => {
      setMessages((prev) => [
        ...prev,
        { id: Date.now().toString() + '-user', role: 'user', content: variables }
      ])
      setQuery('')
    },
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + '-assistant',
          role: 'assistant',
          content: data.answer,
          intent: data.intent,
          confidence: data.confidence,
          matches: data.matches
        }
      ])
    },
    onError: (error) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + '-error',
          role: 'assistant',
          content: (error as ApiError).message,
          isError: true
        }
      ])
    }
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, chatMutation.isPending])

  const departmentsById = new Map(departments.map((item) => [item.id, item]))
  const facultiesById = new Map(faculties.map((item) => [item.id, item]))
  const filteredStaff = staff.filter((member) => {
    const haystack = [member.full_name, member.rank_role, member.bio, member.specializations.join(' ')]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(deferredSearch.toLowerCase())
  })

  return (
    <main className="chat-layout">
      <div className="chat-main">
        <section className="panel panel--chat panel--accent">
          <div className="panel__header" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem', marginBottom: '0.5rem' }}>
            <span className="eyebrow">Conversational AI</span>
            <h2>Ask the Assistant</h2>
            <p>Your central chat interface for role lookup, staff search, and department location guidance.</p>
          </div>

          <div className="chat-history">
            {!messages.length && !chatMutation.isPending && (
               <div className="empty-state" style={{ margin: 'auto' }}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.5, marginBottom: '1rem' }}>
                  <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
                </svg>
                <p className="status">Send a message or select a prompt below to get started.</p>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={msg.role === 'user' ? 'bubble--user' : 'bubble--assistant'}>
                {msg.role === 'user' ? (
                  <p>{msg.content}</p>
                ) : (
                  <>
                    {msg.intent && (
                      <p className="response__intent">
                        Intent: <strong>{msg.intent}</strong> {msg.confidence != null && !Number.isNaN(Number(msg.confidence)) ? `· Confidence: ${Math.round(Number(msg.confidence) * 100)}%` : ''}
                      </p>
                    )}
                    {msg.isError ? (
                      <p className="status status--error">{msg.content}</p>
                    ) : (
                      <div className="response__answer">{msg.content}</div>
                    )}
                    {msg.matches && msg.matches.length > 0 ? (
                      <div className="result-list">
                        {msg.matches.map((match) => (
                          <article key={match.id} className="result-card">
                            <strong>{match.label}</strong>
                            <span className="muted">{match.details ?? match.kind}</span>
                          </article>
                        ))}
                      </div>
                    ) : null}
                  </>
                )}
              </div>
            ))}

            {chatMutation.isPending && (
               <div className="bubble--assistant">
                 <div className="response__answer" style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', padding: '0.5rem', background: 'transparent' }}>
                   <span className="pulse-dot"></span>
                   <span className="pulse-dot" style={{ animationDelay: '0.2s' }}></span>
                   <span className="pulse-dot" style={{ animationDelay: '0.4s' }}></span>
                 </div>
               </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form
            className="stack"
            style={{ marginTop: '1rem', borderTop: '1px solid var(--border)', paddingTop: '1.5rem' }}
            onSubmit={(event) => {
              event.preventDefault()
              if (!query && chatMutation.isPending) return
              const finalQuery = query || chatPrompts[0]
              chatMutation.mutate(finalQuery)
            }}
          >
            <div className="chips">
              {chatPrompts.map((prompt) => (
                <button
                  key={prompt}
                  className="chip"
                  type="button"
                  onClick={() => {
                    chatMutation.mutate(prompt)
                  }}
                >
                  {prompt}
                </button>
              ))}
            </div>
            
            <div className="chat-input-wrapper">
              <textarea
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                rows={1}
                style={{ overflow: 'hidden' }}
                placeholder={chatPrompts[0]}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    if (query || !chatMutation.isPending) {
                      chatMutation.mutate(query || chatPrompts[0])
                    }
                  }
                }}
              />
              <button 
                className="button button--primary" 
                type="submit" 
                disabled={chatMutation.isPending || (!query && chatMutation.isPending)}
                style={{ padding: '0 1rem', height: '44px', flexShrink: 0, borderRadius: 'calc(var(--radius-lg) - 4px)' }}
              >
                {chatMutation.isPending ? '...' : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                  </svg>
                )}
              </button>
            </div>
          </form>
        </section>
      </div>

      <aside className="chat-sidebar">
        <section className="panel" style={{ height: '100%', maxHeight: 'calc(100vh - 180px)', overflowY: 'auto' }}>
          <div className="panel__header">
            <span className="eyebrow">Real-time DB</span>
            <h2>Directory</h2>
          </div>
          <input
            className="input"
            value={directorySearch}
            onChange={(event) => {
              const nextValue = event.target.value
              startTransition(() => setDirectorySearch(nextValue))
            }}
            placeholder="Search staff, roles..."
            style={{ marginBottom: '1rem' }}
          />
          <div className="directory">
            {filteredStaff.slice(0, 10).map((member) => {
              const department = member.department_id ? departmentsById.get(member.department_id) : undefined
              const faculty = member.faculty_id ? facultiesById.get(member.faculty_id) : undefined
              return (
                <article key={member.id} className="directory__card" style={{ padding: '1rem' }}>
                  <div className="record__details">
                    <h3 style={{ fontSize: '1rem' }}>{labelName(member)}</h3>
                    <span className="eyebrow" style={{ marginBottom: 0, fontSize: '0.75rem' }}>{member.rank_role ?? 'Staff member'}</span>
                  </div>
                  <p className="muted" style={{ fontSize: '0.85rem' }}>{department?.name ?? faculty?.name ?? 'University-wide'}</p>
                </article>
              )
            })}
          </div>
        </section>
      </aside>
    </main>
  )
}
