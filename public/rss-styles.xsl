<?xml version="1.0" encoding="UTF-8"?>
<!--
  Folha de estilo do feed RSS.

  Um navegador que abre /rss.xml sem isto mostra XML cru, o que parece erro
  para quem não é técnico. Com esta folha, a mesma URL vira uma página legível
  explicando o que é o feed e como assinar. Leitores de RSS ignoram a folha e
  continuam lendo o XML normalmente.

  Tokens copiados do design system: fundo #050505, texto neutral-400 (#a3a3a3),
  títulos neutral-200 (#e5e5e5), bordas #262626, mono, grid tático de 40px.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <meta name="robots" content="noindex"/>
        <title><xsl:value-of select="/rss/channel/title"/> &#8212; RSS</title>
        <link rel="icon" type="image/png" href="/delta-favicon.png"/>
        <style>
          *{box-sizing:border-box;}
          body{
            margin:0; padding:0;
            background-color:#050505;
            background-image:
              linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(255,255,255,0.02) 1px, transparent 1px);
            background-size:40px 40px;
            color:#a3a3a3;
            font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;
            font-size:14px; line-height:1.65;
            -webkit-font-smoothing:antialiased;
          }
          ::selection{background:#262626;color:#fff;}
          .wrap{max-width:820px;margin:0 auto;padding:56px 20px 80px;}
          a{color:inherit;text-decoration:none;transition:color .2s,border-color .2s;}

          .tag{
            display:inline-block;font-size:10px;letter-spacing:.2em;text-transform:uppercase;
            color:#525252;border:1px solid #262626;padding:4px 9px;margin-bottom:22px;
          }
          h1{
            margin:0 0 10px;color:#e5e5e5;font-size:clamp(1.5rem,4vw,2.1rem);
            font-weight:700;text-transform:uppercase;letter-spacing:-.03em;
          }
          .sub{margin:0 0 28px;color:#737373;max-width:62ch;}

          .how{border:1px solid #262626;background:rgba(255,255,255,.015);padding:18px 20px;margin-bottom:14px;}
          .how h2{margin:0 0 10px;color:#e5e5e5;font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;}
          .how p{margin:0 0 10px;color:#a3a3a3;}
          .how p:last-child{margin-bottom:0;}
          .url{
            display:block;border:1px solid #262626;background:#0a0a0a;color:#e5e5e5;
            padding:11px 13px;margin:12px 0;word-break:break-all;font-size:13px;
          }
          .url:hover{border-color:#525252;}

          .count{font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:#525252;margin:34px 0 14px;}

          .item{border:1px solid #262626;background:rgba(255,255,255,.015);padding:20px;margin-bottom:10px;transition:border-color .2s;}
          .item:hover{border-color:#525252;}
          .meta{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#525252;margin-bottom:9px;}
          .item h3{margin:0 0 9px;font-size:15px;line-height:1.35;color:#e5e5e5;font-weight:700;text-transform:none;letter-spacing:-.01em;}
          .item a.t:hover h3{color:#fff;}
          .item p{margin:0;color:#737373;font-size:13px;}

          .foot{margin-top:44px;padding-top:22px;border-top:1px solid #262626;font-size:11px;letter-spacing:.06em;color:#525252;}
          .foot a{border-bottom:1px solid #262626;}
          .foot a:hover{color:#e5e5e5;border-color:#525252;}

          @media (max-width:640px){ .wrap{padding:34px 16px 60px;} }
        </style>
      </head>
      <body>
        <div class="wrap">

          <span class="tag">RSS Feed</span>
          <h1><xsl:value-of select="/rss/channel/title"/></h1>
          <p class="sub"><xsl:value-of select="/rss/channel/description"/></p>

          <div class="how">
            <h2>What this page is</h2>
            <p>
              This is an RSS feed. Paste the address below into a feed reader
              &#8212; Feedly, NetNewsWire, Thunderbird, or a Discord/Slack bot
              &#8212; and every new report lands there automatically.
            </p>
            <p>
              No email, no signup, nothing collected. You subscribe; we never
              learn who you are.
            </p>
            <a class="url">
              <xsl:attribute name="href"><xsl:value-of select="/rss/channel/link"/>rss.xml</xsl:attribute>
              <xsl:value-of select="/rss/channel/link"/>rss.xml
            </a>
          </div>

          <p class="count">
            <xsl:value-of select="count(/rss/channel/item)"/> reports in this feed
          </p>

          <xsl:for-each select="/rss/channel/item">
            <div class="item">
              <div class="meta">
                <xsl:value-of select="substring(pubDate,6,11)"/>
                <xsl:if test="category">
                  <xsl:text> &#183; </xsl:text>
                  <xsl:value-of select="category[2]"/>
                </xsl:if>
              </div>
              <a class="t">
                <xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute>
                <h3><xsl:value-of select="title"/></h3>
              </a>
              <p><xsl:value-of select="description"/></p>
            </div>
          </xsl:for-each>

          <div class="foot">
            <a>
              <xsl:attribute name="href"><xsl:value-of select="/rss/channel/link"/></xsl:attribute>
              &#8592; Back to <xsl:value-of select="/rss/channel/link"/>
            </a>
          </div>

        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
