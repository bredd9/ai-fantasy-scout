package com.fantasyscout.scout_app;

import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
public class FantasyController {

    private final double BUGET_INITIAL = 500_000_000.0;

    @GetMapping("/")
    public String index(HttpSession session, Model model) {
        // Inițializăm bugetul și echipa dacă e prima dată când intră pe site
        if (session.getAttribute("buget") == null) {
            session.setAttribute("buget", BUGET_INITIAL);
            session.setAttribute("echipa", new ArrayList<Map<String, String>>());
        }

        actualizeazaModel(session, model);
        return "index"; // Numele fișierului HTML pe care îl va căuta (fără extensie)
    }

    @PostMapping("/evalueaza-si-cumpara")
    public String evalueazaSiCumpara(
            @RequestParam String nume,
            @RequestParam int varsta,
            @RequestParam int meciuri,
            @RequestParam int goluri,
            @RequestParam int pase,
            @RequestParam int ovr,
            @RequestParam int pot,
            @RequestParam String pozitie,
            HttpSession session,
            Model model) {

        // 1. Pregătim datele pentru a le trimite la Python (AI)
        Map<String, Object> cererePython = new HashMap<>();
        cererePython.put("varsta", varsta);
        cererePython.put("meciuri", meciuri);
        cererePython.put("goluri", goluri);
        cererePython.put("pase_gol", pase);
        cererePython.put("ovr", ovr);
        cererePython.put("pot", pot);
        cererePython.put("pozitie", pozitie);

        // Clasa din Spring pentru a face cereri HTTP (către portul 5000 al Python-ului)
        RestTemplate restTemplate = new RestTemplate();
        String pythonUrl = "http://127.0.0.1:5000/predict";

        try {
            // Trimitem cererea la Python și așteptăm răspunsul
            Map<String, Object> raspunsPython = restTemplate.postForObject(pythonUrl, cererePython, Map.class);

            // Extragem rezultatele din răspunsul AI-ului
            double pretEstimat = (Double) raspunsPython.get("valoare_estimata");
            String pretFormatat = (String) raspunsPython.get("valoare_formatata");

            // 2. Logica de Joc: Verificăm dacă avem buget
            double bugetCurent = (Double) session.getAttribute("buget");
            if (bugetCurent >= pretEstimat) {
                // Cumpărăm jucătorul (scădem bugetul)
                session.setAttribute("buget", bugetCurent - pretEstimat);

                // Adăugăm jucătorul în listă (pe teren)
                List<Map<String, String>> echipa = (List<Map<String, String>>) session.getAttribute("echipa");
                Map<String, String> jucatorNou = new HashMap<>();
                jucatorNou.put("nume", nume);
                jucatorNou.put("pozitie", pozitie);
                jucatorNou.put("pret", pretFormatat);
                echipa.add(jucatorNou);

                model.addAttribute("mesaj_succes", "Transfer reușit! " + nume + " a fost adus pentru " + pretFormatat);
            } else {
                model.addAttribute("mesaj_eroare", "Fonduri insuficiente! AI-ul cere " + pretFormatat + " pentru acest jucător.");
            }

        } catch (Exception e) {
            model.addAttribute("mesaj_eroare", "Eroare de conexiune cu Scouter-ul AI! Asigură-te că scriptul Python (app.py) rulează în fundal.");
        }

        actualizeazaModel(session, model);
        return "index"; // Întoarcem utilizatorul pe pagina principală
    }

    // Funcție ajutătoare pentru a trimite variabilele mereu către pagina HTML
    private void actualizeazaModel(HttpSession session, Model model) {
        double buget = (Double) session.getAttribute("buget");
        model.addAttribute("buget_formatat", String.format("€%,.2f", buget));
        model.addAttribute("procent_buget", (buget / BUGET_INITIAL) * 100);
        model.addAttribute("echipa", session.getAttribute("echipa"));
    }
}