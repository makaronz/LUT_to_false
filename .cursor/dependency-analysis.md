# Dependency Analysis for site2data

## Project Structure
The repository is organized as a monorepo with multiple workspaces:
- `frontend`: React-based UI
- `backend`: Express-based API server
- `apps/api`: tRPC API server
- `apps/worker-js`: JavaScript worker service
- `apps/worker-py`: Python worker service (package.json not found)
- `packages/types`: Shared TypeScript types
- `packages/utils`: Shared utility functions
- `mobile`: Mobile application

## Frontend Stack
- **Framework**: React 18.2.0
- **Build Tool**: Vite 6.3.3
- **State Management**: Zustand 4.5.0
- **UI Libraries**: 
  - Material UI (MUI) 7.1.0
  - Headless UI 1.7.18
  - React Icons 4.12.0
- **Routing**: React Router DOM 6.22.1
- **HTTP Client**: Axios 1.3.4
- **Visualization**: 
  - Sigma 2.4.0
  - React Sigma 3.4.2
  - ReactFlow 11.11.4
- **Testing**: 
  - Vitest 3.1.2
  - Testing Library React 14.2.1
- **TypeScript**: 5.3.3

## Backend Stack
- **Framework**: Express 4.18.2 (backend), Express 5.1.0 (apps/api)
- **API**: 
  - REST (Express)
  - tRPC 10.43.0 (apps/api)
- **Websockets**: ws 8.18.1
- **Database**: 
  - MongoDB via Mongoose 8.14.1
  - Redis via ioredis 5.4.1/5.6.1
  - Minio 8.0.0 (object storage)
  - Weaviate 2.2.0 (vector database)
- **Validation**: 
  - Zod 3.24.3/3.23.8
  - Ajv 8.17.1/8.16.0
- **PDF Processing**:
  - pdf-lib 1.17.1
  - pdf-parse 1.1.1
  - pdfkit 0.17.1
- **AI/ML**:
  - OpenAI 4.0.0/4.47.1/4.96.0
  - LangChain 0.2.5/0.3.24
- **Logging**: 
  - Winston 3.11.0
  - Pino 9.0.0
- **Security**: 
  - Helmet 8.1.0
  - Express Rate Limit 7.5.0
- **TypeScript**: 5.0.4/5.3.3

## Version Inconsistencies
- **Zod**: 3.24.3 (root, backend, apps/api) vs 3.23.8 (worker-js)
- **OpenAI**: 4.0.0 (backend) vs 4.47.1 (worker-js) vs 4.96.0 (root)
- **Express**: 4.18.2 (backend) vs 5.1.0 (apps/api) - Major version difference
- **TypeScript**: 5.0.4 (backend) vs 5.3.3 (frontend, root, apps/api, worker-js)
- **Testing Library React**: 14.2.1 (frontend) vs 16.3.0 (backend) - Major version difference

## Communication Patterns
- REST APIs (Express)
- tRPC (apps/api)
- WebSockets (ws)
- Redis for pub/sub or caching
- MongoDB for persistence
- Weaviate for vector search
- Minio for object storage

## Potential Risk Areas
1. Version inconsistencies across packages
2. Multiple validation libraries (Zod and Ajv)
3. Multiple PDF processing libraries
4. Express version mismatch (4.x vs 5.x)
5. Multiple state management approaches (React Query in root, Zustand in frontend)
6. Multiple testing frameworks
7. WebSocket communication with frontend
8. Integration between tRPC and Express APIs
