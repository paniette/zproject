<template>
  <Teleport to="body">
    <Transition name="donate-fade">
      <div v-if="show" class="donate-overlay" @click.self="$emit('close')">
        <div class="donate-modal" role="dialog" :aria-label="$t('donate.title')" aria-modal="true">

          <button class="donate-close" :aria-label="$t('common.close')" @click="$emit('close')">✕</button>

          <div class="donate-header">
            <span class="donate-heart-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="38" height="38" fill="currentColor"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
            </span>
            <h2 class="donate-title">{{ $t('donate.title') }}</h2>
            <p class="donate-subtitle">{{ $t('donate.subtitle') }}</p>
          </div>

          <div class="donate-body">
            <div class="donate-left">
              <p class="donate-intro">{{ $t('donate.intro') }}</p>

              <ul class="donate-features">
                <li v-for="feat in features" :key="feat">
                  <span class="donate-feat-icon" aria-hidden="true">{{ feat.icon }}</span>
                  <span>{{ $t(feat.key) }}</span>
                </li>
              </ul>

              <div class="donate-perks-block">
                <p class="donate-perks-title">{{ $t('donate.perksTitle') }}</p>
                <ul class="donate-perks">
                  <li v-for="perk in perks" :key="perk">
                    <span class="donate-perk-bullet" aria-hidden="true">✦</span>
                    <span>{{ $t(perk) }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <aside class="donate-right" aria-label="PayPal">
              <div class="donate-qr">
                <img class="donate-qr-img" src="/qrcode.png" :alt="$t('donate.qrAlt')" loading="lazy" />
                <p class="donate-qr-hint">{{ $t('donate.qrHint') }}</p>
              </div>
            </aside>
          </div>

          <div class="donate-footer">
            <a
              class="donate-btn"
              href="https://www.paypal.me/paniette"
              target="_blank"
              rel="noopener noreferrer"
              :aria-label="$t('donate.cta')"
            >
              <svg class="donate-btn-icon" viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
              {{ $t('donate.cta') }}
            </a>
            <p class="donate-note">{{ $t('donate.note') }}</p>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false }
})
defineEmits(['close'])

const features = [
  { icon: '⚙️', key: 'donate.feat1' },
  { icon: '☁️', key: 'donate.feat2' },
  { icon: '🔐', key: 'donate.feat3' },
  { icon: '🗺️', key: 'donate.feat4' }
]

const perks = ['donate.perk1', 'donate.perk2']
</script>

<style scoped>
.donate-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  backdrop-filter: blur(3px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.donate-modal {
  position: relative;
  background: linear-gradient(160deg, #1e1510 0%, #2a1f17 50%, #1a1a22 100%);
  border: 1px solid rgba(200, 120, 50, 0.35);
  border-radius: 12px;
  width: 100%;
  max-width: 760px;
  max-height: min(90vh, 780px);
  display: flex;
  flex-direction: column;
  box-shadow:
    0 0 0 1px rgba(200, 120, 50, 0.12),
    0 24px 60px rgba(0, 0, 0, 0.7),
    0 0 40px rgba(180, 60, 60, 0.08);
  color: rgba(255, 255, 255, 0.92);
  overflow: hidden;
}

.donate-close {
  position: absolute;
  top: 12px;
  right: 14px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.45);
  font-size: 16px;
  cursor: pointer;
  line-height: 1;
  padding: 4px 6px;
  border-radius: 4px;
  transition: color 0.2s, background 0.2s;
  z-index: 1;
}

.donate-close:hover {
  color: white;
  background: rgba(255, 255, 255, 0.08);
}

.donate-header {
  padding: 32px 32px 20px;
  text-align: center;
  border-bottom: 1px solid rgba(200, 120, 50, 0.18);
}

.donate-heart-icon {
  display: inline-block;
  color: #e05555;
  margin-bottom: 10px;
  filter: drop-shadow(0 0 8px rgba(220, 70, 70, 0.55));
  animation: donate-pulse 2.4s ease-in-out infinite;
}

@keyframes donate-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}

.donate-title {
  font-family: 'Creepster', cursive;
  font-size: 1.8rem;
  font-weight: normal;
  color: var(--primary-color, #c87832);
  margin: 0 0 6px;
  letter-spacing: 0.02em;
}

.donate-subtitle {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  font-style: italic;
}

.donate-body {
  padding: 22px 32px;
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 18px;
  align-items: start;
  overflow: auto;
}

.donate-left {
  min-width: 0;
}

.donate-right {
  position: sticky;
  top: 0;
  align-self: start;
}

.donate-intro {
  font-size: 0.92rem;
  color: rgba(255, 255, 255, 0.78);
  margin: 0 0 18px;
  line-height: 1.55;
}

.donate-features {
  list-style: none;
  margin: 0 0 22px;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.donate-features li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 0.88rem;
  color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(200, 120, 50, 0.14);
  border-radius: 7px;
  padding: 9px 12px;
  line-height: 1.45;
}

.donate-feat-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
  margin-top: 1px;
}

.donate-perks-block {
  background: rgba(200, 120, 50, 0.07);
  border: 1px solid rgba(200, 120, 50, 0.2);
  border-radius: 8px;
  padding: 14px 16px;
}

.donate-qr {
  margin-top: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.donate-qr-img {
  width: 100%;
  max-width: 220px;
  height: auto;
  border-radius: 10px;
  border: 1px solid rgba(200, 120, 50, 0.22);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.35);
  background: rgba(255, 255, 255, 0.92);
}

.donate-qr-hint {
  margin: 0;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
  text-align: center;
}

.donate-perks-title {
  font-size: 0.8rem;
  color: var(--primary-color, #c87832);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
  margin: 0 0 10px;
}

.donate-perks {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.donate-perks li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.45;
}

.donate-perk-bullet {
  color: var(--primary-color, #c87832);
  flex-shrink: 0;
  font-size: 0.7rem;
  margin-top: 3px;
}

.donate-footer {
  padding: 18px 32px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  border-top: 1px solid rgba(200, 120, 50, 0.18);
  flex: 0 0 auto;
}

.donate-btn {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 12px 28px;
  background: linear-gradient(135deg, #c0392b 0%, #e05555 100%);
  color: white;
  border-radius: 50px;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  box-shadow: 0 4px 18px rgba(200, 50, 50, 0.38);
  transition: transform 0.18s, box-shadow 0.18s, filter 0.18s;
}

.donate-btn:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 28px rgba(200, 50, 50, 0.5);
  filter: brightness(1.1);
}

.donate-btn:active {
  transform: translateY(0) scale(0.99);
}

.donate-btn-icon {
  flex-shrink: 0;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.3));
}

.donate-note {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.38);
  text-align: center;
  margin: 0;
  font-style: italic;
}

/* Transition */
.donate-fade-enter-active,
.donate-fade-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.donate-fade-enter-from,
.donate-fade-leave-to {
  opacity: 0;
}

.donate-fade-enter-from .donate-modal,
.donate-fade-leave-to .donate-modal {
  transform: scale(0.95) translateY(10px);
}

@media (max-width: 540px) {
  .donate-header,
  .donate-body,
  .donate-footer {
    padding-left: 20px;
    padding-right: 20px;
  }

  .donate-body {
    grid-template-columns: 1fr;
  }

  .donate-right {
    position: static;
    order: 2;
  }

  .donate-title {
    font-size: 1.5rem;
  }
}
</style>
