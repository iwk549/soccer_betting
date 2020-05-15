stats_page_base = """<!DOCTYPE HTML>

<html>
    <head>
        <title>
            Soccer Betting
        </title>
        <link href="../../stylesheet.css" rel="stylesheet">
    </head>
    
    <body>
        <div class="sidenav">
            <br>
            <a href="http://www.dosshouse.us">Dosshouse Home</a><br><br>
            <button type="button" class="not_collapsible" style="font-size:1em;">Leagues</button>
                <div class="not_content">
                <button type="button" class="collapsible" style="font-size: .75em;">England</button>
                    <div class="content" style="font-size: 0.6em;">
                        <a href="http://www.dosshouse.us/soccer_betting/english_premier_league/stats.html">Current Stats</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/english_premier_league/matches.html">Upcoming Matches</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/english_premier_league/archived_bets.html">Archive</a><br />
                    </div>
                    
                    <button type="button" class="collapsible" style="font-size: .75em;">France</button>
                    <div class="content" style="font-size: 0.6em;">
                        <a href="http://www.dosshouse.us/soccer_betting/french_ligue_1/stats.html">Current Stats</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/french_ligue_1/matches.html">Upcoming Matches</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/french_ligue_1/archived_bets.html">Archive</a><br />
                    </div>
                    
                    <button type="button" class="collapsible" style="font-size: .75em;">Germany</button>
                    <div class="content" style="font-size: 0.6em;">
                        <a href="http://www.dosshouse.us/soccer_betting/german_bundesliga/stats.html">Current Stats</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/german_bundesliga/matches.html">Upcoming Matches</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/german_bundesliga/archived_bets.html">Archive</a><br />
                    </div>
                    
                    <button type="button" class="collapsible" style="font-size: .75em;">Italy</button>
                    <div class="content" style="font-size: 0.6em;">
                        <a href="http://www.dosshouse.us/soccer_betting/italian_serie_a/stats.html">Current Stats</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/italian_serie_a/matches.html">Upcoming Matches</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/italian_serie_a/archived_bets.html">Archive</a><br />
                    </div>
                    
                    <button type="button" class="collapsible" style="font-size: .75em;">Spain</button>
                    <div class="content" style="font-size: 0.6em;">
                        <a href="http://www.dosshouse.us/soccer_betting/spanish_la_liga/stats.html">Current Stats</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/spanish_la_liga/matches.html">Upcoming Matches</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/spanish_la_liga/archived_bets.html">Archive</a><br />
                    </div>
                </div>
        </div>
        
        <div class="table">
"""


stats_page_after_tables = """</div>
        <footer class="source">
            <p>Source: <a href="http://www.understat.com">understat.com&nbsp;</a><br />
            Last updated """


stats_page_script = """&nbsp;</p></footer>
        
        <script>
            var col1 = document.getElementsByClassName("collapsible");
            var i;
            for (i = 0; i < col1.length; i++) {
                col1[i].addEventListener("click", function() {
                    this.classList.toggle("active");
                    var content = this.nextElementSibling;
                    if (content.style.display === "block") {
                        content.style.display = "none";
                    } else {
                        content.style.display = "block";
                    }
                });
            }
            function sortTable(n, tableName) {
              var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
              table = document.getElementById(tableName);
              switching = true;
              //Set the sorting direction to ascending:
              dir = "asc"; 
              /*Make a loop that will continue until
              no switching has been done:*/
              while (switching) {
                //start by saying: no switching is done:
                switching = false;
                rows = table.rows;
                /*Loop through all table rows (except the
                first, which contains table headers):*/
                for (i = 1; i < (rows.length - 1); i++) {
                  //start by saying there should be no switching:
                  shouldSwitch = false;
                  /*Get the two elements you want to compare,
                  one from current row and one from the next:*/
                  x = rows[i].getElementsByTagName("TD")[n].innerHTML.toLowerCase();
                  y = rows[i + 1].getElementsByTagName("TD")[n].innerHTML.toLowerCase();
                  /*check if the two rows should switch place,
                  based on the direction, asc or desc:*/
                  if (Number.isInteger(parseFloat(x))) {
                      x = parseFloat(x)
                      y = parseFloat(y)
                  }
                  if (dir == "asc") {
                    if (x > y) {
                      //if so, mark as a switch and break the loop:
                      shouldSwitch= true;
                      break;
                    }
                  } else if (dir == "desc") {
                    if (x < y) {
                      //if so, mark as a switch and break the loop:
                      shouldSwitch = true;
                      break;
                    }
                  }
                }
                if (shouldSwitch) {
                  /*If a switch has been marked, make the switch
                  and mark that a switch has been done:*/
                  rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                  switching = true;
                  //Each time a switch is done, increase this count by 1:
                  switchcount ++;      
                } else {
                  /*If no switching has been done AND the direction is "asc",
                  set the direction to "desc" and run the while loop again.*/
                  if (switchcount == 0 && dir == "asc") {
                    dir = "desc";
                    switching = true;
                  }
                }
              }
            }
        </script>
        
    </body>
    """


archive_page_base = """<!DOCTYPE HTML>

<html>
    <head>
        <title>
            Soccer Betting
        </title>
        <link href="../../stylesheet.css" rel="stylesheet">
    </head>

    <body>
        <div class="sidenav">
            <br>
            <a href="http://www.dosshouse.us">Dosshouse Home</a><br><br>
            <button type="button" class="not_collapsible" style="font-size:1em;">Leagues</button>
                <div class="not_content">
                <button type="button" class="collapsible" style="font-size: .75em;">England</button>
                    <div class="content" style="font-size: 0.6em;">
                        <a href="http://www.dosshouse.us/soccer_betting/english_premier_league/stats.html">Current Stats</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/english_premier_league/matches.html">Upcoming Matches</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/english_premier_league/archived_bets.html">Archive</a><br />
                    </div>

                    <button type="button" class="collapsible" style="font-size: .75em;">France</button>
                    <div class="content" style="font-size: 0.6em;">
                        <a href="http://www.dosshouse.us/soccer_betting/french_ligue_1/stats.html">Current Stats</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/french_ligue_1/matches.html">Upcoming Matches</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/french_ligue_1/archived_bets.html">Archive</a><br />
                    </div>

                    <button type="button" class="collapsible" style="font-size: .75em;">Germany</button>
                    <div class="content" style="font-size: 0.6em;">
                        <a href="http://www.dosshouse.us/soccer_betting/german_bundesliga/stats.html">Current Stats</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/german_bundesliga/matches.html">Upcoming Matches</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/german_bundesliga/archived_bets.html">Archive</a><br />
                    </div>

                    <button type="button" class="collapsible" style="font-size: .75em;">Italy</button>
                    <div class="content" style="font-size: 0.6em;">
                        <a href="http://www.dosshouse.us/soccer_betting/italian_serie_a/stats.html">Current Stats</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/italian_serie_a/matches.html">Upcoming Matches</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/italian_serie_a/archived_bets.html">Archive</a><br />
                    </div>

                    <button type="button" class="collapsible" style="font-size: .75em;">Spain</button>
                    <div class="content" style="font-size: 0.6em;">
                        <a href="http://www.dosshouse.us/soccer_betting/spanish_la_liga/stats.html">Current Stats</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/spanish_la_liga/matches.html">Upcoming Matches</a><br />
                        <a href="http://www.dosshouse.us/soccer_betting/spanish_la_liga/archived_bets.html">Archive</a><br />
                    </div>
                </div>
        </div>

        <div class="table">
"""


archive_page_after_tables = """</div>
        <footer class="source">
            <p>Source: <a href="http://www.bovada.lv">bovada.lv&nbsp;</a><br />
            Last updated """


archive_page_script = """&nbsp;</p></footer>

        <script>
            var col1 = document.getElementsByClassName("collapsible");
            var i;
            for (i = 0; i < col1.length; i++) {
                col1[i].addEventListener("click", function() {
                    this.classList.toggle("active");
                    var content = this.nextElementSibling;
                    if (content.style.display === "block") {
                        content.style.display = "none";
                    } else {
                        content.style.display = "block";
                    }
                });
            }
            
            function sortTable(n, tableName) {
              var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
              table = document.getElementById(tableName);
              switching = true;
              //Set the sorting direction to ascending:
              dir = "asc"; 
              /*Make a loop that will continue until
              no switching has been done:*/
              while (switching) {
                //start by saying: no switching is done:
                switching = false;
                rows = table.rows;
                /*Loop through all table rows (except the
                first, which contains table headers):*/
                for (i = 1; i < (rows.length - 1); i++) {
                  //start by saying there should be no switching:
                  shouldSwitch = false;
                  /*Get the two elements you want to compare,
                  one from current row and one from the next:*/
                  x = rows[i].getElementsByTagName("TD")[n].innerHTML.toLowerCase();
                  y = rows[i + 1].getElementsByTagName("TD")[n].innerHTML.toLowerCase();
                  /*check if the two rows should switch place,
                  based on the direction, asc or desc:*/
                  if (Number.isInteger(parseFloat(x))) {
                      x = parseFloat(x)
                      y = parseFloat(y)
                  }
                  if (dir == "asc") {
                    if (x > y) {
                      //if so, mark as a switch and break the loop:
                      shouldSwitch= true;
                      break;
                    }
                  } else if (dir == "desc") {
                    if (x < y) {
                      //if so, mark as a switch and break the loop:
                      shouldSwitch = true;
                      break;
                    }
                  }
                }
                if (shouldSwitch) {
                  /*If a switch has been marked, make the switch
                  and mark that a switch has been done:*/
                  rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                  switching = true;
                  //Each time a switch is done, increase this count by 1:
                  switchcount ++;      
                } else {
                  /*If no switching has been done AND the direction is "asc",
                  set the direction to "desc" and run the while loop again.*/
                  if (switchcount == 0 && dir == "asc") {
                    dir = "desc";
                    switching = true;
                  }
                }
              }
            }
            
            function searchFunction() {
              var input, filter, table, tr, td, i, txtValue;
              input = document.getElementById("myInput");
              filter = input.value.toUpperCase();
              table = document.getElementById("stats_table");
              tr = table.getElementsByTagName("tr");
              for (i = 0; i < tr.length; i++) {
                td = tr[i].getElementsByTagName("td")[11];
                if (td) {
                  txtValue = td.textContent || td.innerText;
                  if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                  } else {
                    tr[i].style.display = "none";
      }
    }       
  }
}
        </script>
        
    </body>
    """