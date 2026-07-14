// ==========================================
// CONFIGURACIÓN DE SUPABASE
// ==========================================
// Pega aquí tu URL de Supabase
const SUPABASE_URL = 'https://lttgrfsanyjsmxqaoche.supabase.co';
// Pega aquí tu "anon / public key" (La encuentras en Supabase -> Settings -> API)
const SUPABASE_ANON_KEY = 'sb_publishable_E2SUpqGKjD918wNLF85nAA_G-jKU5aJ';

const db = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// ==========================================
// ELEMENTOS DEL DOM
// ==========================================
const grid = document.getElementById('inmuebles-grid');
const loader = document.getElementById('loader');
const emptyState = document.getElementById('empty-state');
const countBadge = document.getElementById('total-count');

// ==========================================
// LÓGICA PRINCIPAL
// ==========================================

async function fetchInmuebles() {
    try {
        // Traemos todos los inmuebles que NO estén descartados, ordenados por fecha (más recientes primero)
        // NOTA: Si la columna 'discarded' no existe aún, esto puede fallar. Asegúrate de crearla.
        const { data, error } = await db
            .from('inmuebles')
            .select('*')
            .is('discarded', false) // o null si apenas la creas
            .order('date_added', { ascending: false });

        if (error) {
            // Si falla por la columna descartada (porque no existe), intentamos traer todos
            if (error.code === '42703') { 
                console.warn("La columna 'discarded' no existe en Supabase. Cargando todos...");
                const fallback = await db
                    .from('inmuebles')
                    .select('*')
                    .order('date_added', { ascending: false });
                return fallback.data || [];
            }
            throw error;
        }

        return data || [];
    } catch (err) {
        console.error('Error fetching inmuebles:', err);
        alert('Error al conectar con la base de datos. Verifica tu ANON_KEY.');
        return [];
    }
}

function renderCards(inmuebles) {
    loader.classList.add('hidden');
    
    if (inmuebles.length === 0) {
        emptyState.classList.remove('hidden');
        grid.classList.add('hidden');
        countBadge.textContent = '0 inmuebles';
        return;
    }

    countBadge.textContent = `${inmuebles.length} inmuebles`;
    grid.innerHTML = '';
    
    inmuebles.forEach(inmueble => {
        const card = document.createElement('div');
        card.className = 'card';
        card.id = `card-${inmueble.id}`;

        // Limpiar un poco el título
        let title = inmueble.title;
        let isStarred = title.includes('⭐');
        if (isStarred) title = title.replace('⭐', '').trim();

        const badgeHtml = inmueble.is_agency ? `<span class="card-badge">Inmobiliaria</span>` : '';
        const starHtml = isStarred ? `⭐ ` : '';

        card.innerHTML = `
            ${badgeHtml}
            <h3 class="card-title">${starHtml}${title}</h3>
            <div class="card-price">${inmueble.price}</div>
            
            <div class="card-details">
                <div class="detail-item">
                    <span>📍</span> Extraído de: ${inmueble.source || (inmueble.url.includes('ciencuadras') ? 'CienCuadras' : (inmueble.url.includes('metrocuadrado') ? 'MetroCuadrado' : 'Arriendo.com'))}
                </div>
                <div class="detail-item">
                    <span>📅</span> Detectado: ${new Date(inmueble.date_added).toLocaleDateString()}
                </div>
            </div>

            <div class="card-actions">
                <a href="${inmueble.url}" target="_blank" rel="noopener" class="btn btn-primary">Ver Original</a>
                <button onclick="discardInmueble('${inmueble.id}')" class="btn btn-danger">Descartar</button>
            </div>
        `;
        
        grid.appendChild(card);
    });

    grid.classList.remove('hidden');
    emptyState.classList.add('hidden');
}

async function discardInmueble(id) {
    // UI Optimistic Update
    const card = document.getElementById(`card-${id}`);
    if (card) {
        card.style.opacity = '0.5';
        card.style.pointerEvents = 'none';
        card.querySelector('.btn-danger').textContent = 'Descartando...';
    }

    try {
        const { error } = await db
            .from('inmuebles')
            .update({ discarded: true })
            .eq('id', id);

        if (error) {
            // Si la columna no existe, mostramos error
            if(error.code === '42703') {
                alert("Debes crear la columna 'discarded' (tipo Boolean) en Supabase para poder ocultarlos.");
            } else {
                throw error;
            }
            // Revertir UI
            if (card) {
                card.style.opacity = '1';
                card.style.pointerEvents = 'auto';
                card.querySelector('.btn-danger').textContent = 'Descartar';
            }
            return;
        }

        // Animar salida
        if (card) {
            card.style.transform = 'scale(0.9)';
            card.style.opacity = '0';
            setTimeout(() => {
                card.remove();
                // Actualizar contador
                const currentCount = document.querySelectorAll('.card').length;
                countBadge.textContent = `${currentCount} inmuebles`;
                if (currentCount === 0) {
                    grid.classList.add('hidden');
                    emptyState.classList.remove('hidden');
                }
            }, 300);
        }
    } catch (err) {
        console.error('Error discarding:', err);
        alert('Error al descartar. Revisa la consola.');
    }
}

// ==========================================
// INICIALIZACIÓN
// ==========================================
document.addEventListener('DOMContentLoaded', async () => {
    if (SUPABASE_ANON_KEY === 'PEGA_TU_ANON_KEY_AQUI') {
        alert("¡Falta configurar tu ANON_KEY en app.js!");
        loader.classList.add('hidden');
        return;
    }
    
    const inmuebles = await fetchInmuebles();
    renderCards(inmuebles);
});
