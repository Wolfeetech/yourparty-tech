<?php
/**
 * Template Name: Impressum
 *
 * @package YourParty_Tech
 */

get_header();
?>

<div class="container section">
    <div class="legal-content">
        <h1>Impressum</h1>

        <h2>Angaben gem  5 TMG</h2>
        <p>
            <strong>YourParty Tech</strong><br>
            Wolfgang Prinz<br>
            Stockenweiler 3<br>
            88138 Hergensweiler<br>
            Deutschland
        </p>

        <h2>Kontakt</h2>
        <p>
            E-Mail: <a href="mailto:wolf@yourparty.tech">wolf@yourparty.tech</a><br>
            Internet: <a href="https://yourparty.tech">https://yourparty.tech</a>
        </p>

        <h2>Redaktionell Verantwortlicher</h2>
        <p>
            Wolfgang Prinz<br>
            Stockenweiler 3<br>
            88138 Hergensweiler
        </p>

        <h2>EU-Streitschlichtung</h2>
        <p>
            Die Europische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: 
            <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr/</a>.<br>
            Unsere E-Mail-Adresse finden Sie oben im Impressum.
        </p>

        <h2>Verbraucherstreitbeilegung/Universalschlichtungsstelle</h2>
        <p>
            Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.
        </p>

        <hr class="legal-divider">

        <h2>Haftung fr Inhalte</h2>
        <p>
            Als Diensteanbieter sind wir gem  7 Abs.1 TMG fr eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. 
            Nach  8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, bermittelte oder gespeicherte fremde Informationen zu 
            berwachen oder nach Umstnden zu forschen, die auf eine rechtswidrige Ttigkeit hinweisen.
            Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberhrt. 
            Eine diesbezgliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung mglich. Bei Bekanntwerden 
            von entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.
        </p>

        <h2>Haftung fr Links</h2>
        <p>
            Unser Angebot enthlt Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Deshalb knnen wir fr diese 
            fremden Inhalte auch keine Gewhr bernehmen. Fr die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber 
            der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mgliche Rechtsverste berprft. Rechtswidrige 
            Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar.
            Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. 
            Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.
        </p>

        <h2>Urheberrecht</h2>
        <p>
            Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Vervielfltigung, 
            Bearbeitung, Verbreitung und jede Art der Verwertung auerhalb der Grenzen des Urheberrechtes bedrfen der schriftlichen Zustimmung des 
            jeweiligen Autors bzw. Erstellers. Downloads und Kopien dieser Seite sind nur fr den privaten, nicht kommerziellen Gebrauch gestattet.
            Soweit die Inhalte auf dieser Seite nicht vom Betreiber erstellt wurden, werden die Urheberrechte Dritter beachtet. Insbesondere werden 
            Inhalte Dritter als solche gekennzeichnet. Sollten Sie trotzdem auf eine Urheberrechtsverletzung aufmerksam werden, bitten wir um einen 
            entsprechenden Hinweis. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Inhalte umgehend entfernen.
        </p>

        <p class="source-credit">Quelle: <a href="https://www.e-recht24.de" target="_blank">e-recht24.de</a></p>
    </div>
</div>

<style>
    .section { padding: 80px 0; }
    .legal-content { max-width: 800px; margin: 0 auto; color: var(--text-muted); font-family: var(--font-body); }
    .legal-content h1 { color: #fff; font-size: 3rem; margin-bottom: 3rem; letter-spacing: -0.02em; border-bottom: 2px solid var(--border); padding-bottom: 20px; }
    .legal-content h2 { color: var(--emerald); font-size: 1.5rem; margin-top: 3rem; margin-bottom: 1rem; font-family: var(--font-display); text-transform: uppercase; letter-spacing: 0.05em; }
    .legal-content h3 { color: #fff; font-size: 1.1rem; margin-top: 1.5rem; margin-bottom: 0.5rem; }
    .legal-content p { line-height: 1.7; margin-bottom: 1.5rem; font-size: 1.05rem; }
    .legal-content strong { color: #fff; }
    .legal-content a { color: var(--emerald); text-decoration: none; transition: all 0.2s; border-bottom: 1px solid transparent; }
    .legal-content a:hover { color: #fff; border-bottom-color: var(--emerald); }
    .legal-divider { border: 0; border-top: 1px solid var(--border); margin: 40px 0; opacity: 0.5; }
    .source-credit { font-size: 0.8rem; margin-top: 40px; opacity: 0.5; }
</style>

<?php get_footer(); ?>
