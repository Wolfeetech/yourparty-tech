<?php
/**
 * Cookie Consent Banner (GDPR Compliant)
 * 
 * Minimal, professional cookie consent for YourParty Tech.
 * Only essential cookies (session, preferences) - no tracking without consent.
 * 
 * @package YourPartyTech
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Output Cookie Consent HTML
 */
function yourparty_cookie_consent_html() {
    // Don't show if already consented
    if (isset($_COOKIE['yourparty_cookie_consent'])) {
        return;
    }
    ?>
    <div id="cookie-consent" class="cookie-consent" role="dialog" aria-labelledby="cookie-title" aria-describedby="cookie-desc">
        <div class="cookie-consent__inner">
            <div class="cookie-consent__content">
                <h3 id="cookie-title"> Cookie-Hinweis</h3>
                <p id="cookie-desc">
                    Wir verwenden nur technisch notwendige Cookies fr den Radio-Stream und deine Einstellungen. 
                    Keine Werbung, kein Tracking.
                    <a href="<?php echo esc_url(home_url('/datenschutz/')); ?>">Mehr erfahren</a>
                </p>
            </div>
            <div class="cookie-consent__actions">
                <button id="cookie-accept" class="cookie-btn cookie-btn--accept">Verstanden</button>
            </div>
        </div>
    </div>
    <style>
        .cookie-consent {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 99998;
            background: linear-gradient(180deg, rgba(15, 15, 15, 0.98) 0%, rgba(10, 10, 10, 0.99) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            transform: translateY(100%);
            opacity: 0;
            animation: slideUp 0.5s ease-out 0.5s forwards;
        }
        
        @keyframes slideUp {
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        .cookie-consent__inner {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            flex-wrap: wrap;
        }
        
        .cookie-consent__content {
            flex: 1;
            min-width: 280px;
        }
        
        .cookie-consent__content h3 {
            font-size: 1rem;
            font-weight: 700;
            color: #fff;
            margin: 0 0 8px 0;
        }
        
        .cookie-consent__content p {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.7);
            margin: 0;
            line-height: 1.5;
        }
        
        .cookie-consent__content a {
            color: var(--neon-green, #00ff88);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s;
        }
        
        .cookie-consent__content a:hover {
            border-bottom-color: var(--neon-green, #00ff88);
        }
        
        .cookie-consent__actions {
            display: flex;
            gap: 12px;
            flex-shrink: 0;
        }
        
        .cookie-btn {
            padding: 12px 28px;
            border-radius: 24px;
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
        }
        
        .cookie-btn--accept {
            background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
            color: #000;
        }
        
        .cookie-btn--accept:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 255, 136, 0.3);
        }
        
        .cookie-consent.hidden {
            animation: slideDown 0.3s ease-in forwards;
        }
        
        @keyframes slideDown {
            to {
                transform: translateY(100%);
                opacity: 0;
            }
        }
        
        @media (max-width: 600px) {
            .cookie-consent {
                padding: 16px;
            }
            
            .cookie-consent__inner {
                flex-direction: column;
                text-align: center;
            }
            
            .cookie-consent__actions {
                width: 100%;
                justify-content: center;
            }
        }
    </style>
    <script>
        (function() {
            const banner = document.getElementById('cookie-consent');
            const acceptBtn = document.getElementById('cookie-accept');
            
            if (acceptBtn) {
                acceptBtn.addEventListener('click', function() {
                    // Set cookie for 365 days
                    const expires = new Date();
                    expires.setTime(expires.getTime() + (365 * 24 * 60 * 60 * 1000));
                    document.cookie = 'yourparty_cookie_consent=accepted; expires=' + expires.toUTCString() + '; path=/; SameSite=Lax';
                    
                    // Hide banner
                    banner.classList.add('hidden');
                    setTimeout(function() {
                        banner.style.display = 'none';
                    }, 300);
                });
            }
        })();
    </script>
    <?php
}

// Hook into wp_footer to display the consent banner
add_action('wp_footer', 'yourparty_cookie_consent_html', 99);
