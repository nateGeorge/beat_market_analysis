# download folder for firefox should be /home/nate/Dropbox/data/sp600


# TODO: if downloaded file is 0 bytes, try again


# core
import os
import time
import glob
import calendar
import datetime
import shutil
import traceback

# installed
import pytz
import requests as req
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from fake_useragent import UserAgent
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal

# custom
import constituents_utils as cu

# for headless browser mode with FF
# http://scraping.pro/use-headless-firefox-scraping-linux/
# main thing to do is install this first:
# sudo apt-get install xvfb
from pyvirtualdisplay import Display
display = Display(visible=0, size=(1920, 1080))
display.start()

FILEPATH = '/home/nate/Dropbox/data/sp600/'


def make_dirs(path):
    """
    makes directory, one folder at a time
    """
    last_dir = cu.get_home_dir()
    new_path = path
    if last_dir in path:
        new_path = path.replace(last_dir, '')

    for d in new_path.split('/'):
        last_dir = os.path.join(last_dir, d)
        if not os.path.exists(last_dir):
            os.mkdir(last_dir)


def get_last_open_trading_day():
    # use NY time so the day is correct -- should also correct for times after
    # midnight NY time and before market close that day
    today_ny = datetime.datetime.now(pytz.timezone('America/New_York'))
    ndq = mcal.get_calendar('NASDAQ')
    open_days = ndq.schedule(start_date=today_ny - pd.Timedelta(str(3*365) + ' days'), end_date=today_ny)
    # basically, this waits for 3 hours after market close if it's the same day
    return open_days.iloc[-1]['market_close'].date().strftime('%Y-%m-%d')


def check_if_today_trading_day():
    today_ny = datetime.datetime.now(pytz.timezone('America/New_York'))
    ndq = mcal.get_calendar('NASDAQ')
    open_days = ndq.schedule(start_date=today_ny - pd.Timedelta(str(365) + ' days'), end_date=today_ny)
    return open_days.index[-1].date() == today_ny.date()


def setup_driver():
    """
    need to first download and setup geckodriver; instructions here:
    https://stackoverflow.com/a/40208762/4549682
    use geckodriver 0.20.1 until brokenpipeerror bug is fixed: https://github.com/mozilla/geckodriver/issues/1321
    """
    # couldn't get download working without manual settings...
    # https://stackoverflow.com/questions/38307446/selenium-browser-helperapps-neverask-openfile-and-savetodisk-is-not-working
    # create the profile (on ubuntu, firefox -P from command line),
    # download once, check 'don't ask again' and 'save'
    # also change downloads folder to ticker_data within git repo
    # then file path to profile, and use here:
    # investing.com was the name of the profile]
    prof_paths = ['/home/nate/.mozilla/firefox/exzvq4ez.investing.com',
                # work computer path
                '/home/nate/.mozilla/firefox/i12g875t.investing.com']
    found_prof = False
    for p in prof_paths:
        try:
            prof_path = p
        # saves to /home/nate/github/beat_market_analysis folder by default
            profile = webdriver.FirefoxProfile(prof_path)
            found_prof = True
            print('found profile at', p)
        except FileNotFoundError:
            pass

    if found_prof == False:
        print('ERROR: no profile could be found, exiting')
        exit()

    # auto-download unknown mime types:
    # http://forums.mozillazine.org/viewtopic.php?f=38&t=2430485
    # set to text/csv and semicolon-separated any other file types
    # https://stackoverflow.com/a/9329022/4549682
    # list all mimetypes to be safe
    # https://stackoverflow.com/a/34780823/4549682
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', "application/vnd.hzn-3d-crossword;video/3gpp;video/3gpp2;application/vnd.mseq;application/vnd.3m.post-it-notes;application/vnd.3gpp.pic-bw-large;application/vnd.3gpp.pic-bw-small;application/vnd.3gpp.pic-bw-var;application/vnd.3gp2.tcap;application/x-7z-compressed;application/x-abiword;application/x-ace-compressed;application/vnd.americandynamics.acc;application/vnd.acucobol;application/vnd.acucorp;audio/adpcm;application/x-authorware-bin;application/x-athorware-map;application/x-authorware-seg;application/vnd.adobe.air-application-installer-package+zip;application/x-shockwave-flash;application/vnd.adobe.fxp;application/pdf;application/vnd.cups-ppd;application/x-director;applicaion/vnd.adobe.xdp+xml;application/vnd.adobe.xfdf;audio/x-aac;application/vnd.ahead.space;application/vnd.airzip.filesecure.azf;application/vnd.airzip.filesecure.azs;application/vnd.amazon.ebook;application/vnd.amiga.ami;applicatin/andrew-inset;application/vnd.android.package-archive;application/vnd.anser-web-certificate-issue-initiation;application/vnd.anser-web-funds-transfer-initiation;application/vnd.antix.game-component;application/vnd.apple.installe+xml;application/applixware;application/vnd.hhe.lesson-player;application/vnd.aristanetworks.swi;text/x-asm;application/atomcat+xml;application/atomsvc+xml;application/atom+xml;application/pkix-attr-cert;audio/x-aiff;video/x-msvieo;application/vnd.audiograph;image/vnd.dxf;model/vnd.dwf;text/plain-bas;application/x-bcpio;application/octet-stream;image/bmp;application/x-bittorrent;application/vnd.rim.cod;application/vnd.blueice.multipass;application/vnd.bm;application/x-sh;image/prs.btif;application/vnd.businessobjects;application/x-bzip;application/x-bzip2;application/x-csh;text/x-c;application/vnd.chemdraw+xml;text/css;chemical/x-cdx;chemical/x-cml;chemical/x-csml;application/vn.contact.cmsg;application/vnd.claymore;application/vnd.clonk.c4group;image/vnd.dvb.subtitle;application/cdmi-capability;application/cdmi-container;application/cdmi-domain;application/cdmi-object;application/cdmi-queue;applicationvnd.cluetrust.cartomobile-config;application/vnd.cluetrust.cartomobile-config-pkg;image/x-cmu-raster;model/vnd.collada+xml;text/csv;application/mac-compactpro;application/vnd.wap.wmlc;image/cgm;x-conference/x-cooltalk;image/x-cmx;application/vnd.xara;application/vnd.cosmocaller;application/x-cpio;application/vnd.crick.clicker;application/vnd.crick.clicker.keyboard;application/vnd.crick.clicker.palette;application/vnd.crick.clicker.template;application/vn.crick.clicker.wordbank;application/vnd.criticaltools.wbs+xml;application/vnd.rig.cryptonote;chemical/x-cif;chemical/x-cmdf;application/cu-seeme;application/prs.cww;text/vnd.curl;text/vnd.curl.dcurl;text/vnd.curl.mcurl;text/vnd.crl.scurl;application/vnd.curl.car;application/vnd.curl.pcurl;application/vnd.yellowriver-custom-menu;application/dssc+der;application/dssc+xml;application/x-debian-package;audio/vnd.dece.audio;image/vnd.dece.graphic;video/vnd.dec.hd;video/vnd.dece.mobile;video/vnd.uvvu.mp4;video/vnd.dece.pd;video/vnd.dece.sd;video/vnd.dece.video;application/x-dvi;application/vnd.fdsn.seed;application/x-dtbook+xml;application/x-dtbresource+xml;application/vnd.dvb.ait;applcation/vnd.dvb.service;audio/vnd.digital-winds;image/vnd.djvu;application/xml-dtd;application/vnd.dolby.mlp;application/x-doom;application/vnd.dpgraph;audio/vnd.dra;application/vnd.dreamfactory;audio/vnd.dts;audio/vnd.dts.hd;imag/vnd.dwg;application/vnd.dynageo;application/ecmascript;application/vnd.ecowin.chart;image/vnd.fujixerox.edmics-mmr;image/vnd.fujixerox.edmics-rlc;application/exi;application/vnd.proteus.magazine;application/epub+zip;message/rfc82;application/vnd.enliven;application/vnd.is-xpr;image/vnd.xiff;application/vnd.xfdl;application/emma+xml;application/vnd.ezpix-album;application/vnd.ezpix-package;image/vnd.fst;video/vnd.fvt;image/vnd.fastbidsheet;application/vn.denovo.fcselayout-link;video/x-f4v;video/x-flv;image/vnd.fpx;image/vnd.net-fpx;text/vnd.fmi.flexstor;video/x-fli;application/vnd.fluxtime.clip;application/vnd.fdf;text/x-fortran;application/vnd.mif;application/vnd.framemaker;imae/x-freehand;application/vnd.fsc.weblaunch;application/vnd.frogans.fnc;application/vnd.frogans.ltf;application/vnd.fujixerox.ddd;application/vnd.fujixerox.docuworks;application/vnd.fujixerox.docuworks.binder;application/vnd.fujitu.oasys;application/vnd.fujitsu.oasys2;application/vnd.fujitsu.oasys3;application/vnd.fujitsu.oasysgp;application/vnd.fujitsu.oasysprs;application/x-futuresplash;application/vnd.fuzzysheet;image/g3fax;application/vnd.gmx;model/vn.gtw;application/vnd.genomatix.tuxedo;application/vnd.geogebra.file;application/vnd.geogebra.tool;model/vnd.gdl;application/vnd.geometry-explorer;application/vnd.geonext;application/vnd.geoplan;application/vnd.geospace;applicatio/x-font-ghostscript;application/x-font-bdf;application/x-gtar;application/x-texinfo;application/x-gnumeric;application/vnd.google-earth.kml+xml;application/vnd.google-earth.kmz;application/vnd.grafeq;image/gif;text/vnd.graphviz;aplication/vnd.groove-account;application/vnd.groove-help;application/vnd.groove-identity-message;application/vnd.groove-injector;application/vnd.groove-tool-message;application/vnd.groove-tool-template;application/vnd.groove-vcar;video/h261;video/h263;video/h264;application/vnd.hp-hpid;application/vnd.hp-hps;application/x-hdf;audio/vnd.rip;application/vnd.hbci;application/vnd.hp-jlyt;application/vnd.hp-pcl;application/vnd.hp-hpgl;application/vnd.yamaha.h-script;application/vnd.yamaha.hv-dic;application/vnd.yamaha.hv-voice;application/vnd.hydrostatix.sof-data;application/hyperstudio;application/vnd.hal+xml;text/html;application/vnd.ibm.rights-management;application/vnd.ibm.securecontainer;text/calendar;application/vnd.iccprofile;image/x-icon;application/vnd.igloader;image/ief;application/vnd.immervision-ivp;application/vnd.immervision-ivu;application/reginfo+xml;text/vnd.in3d.3dml;text/vnd.in3d.spot;mode/iges;application/vnd.intergeo;application/vnd.cinderella;application/vnd.intercon.formnet;application/vnd.isac.fcs;application/ipfix;application/pkix-cert;application/pkixcmp;application/pkix-crl;application/pkix-pkipath;applicaion/vnd.insors.igm;application/vnd.ipunplugged.rcprofile;application/vnd.irepository.package+xml;text/vnd.sun.j2me.app-descriptor;application/java-archive;application/java-vm;application/x-java-jnlp-file;application/java-serializd-object;text/x-java-source,java;application/javascript;application/json;application/vnd.joost.joda-archive;video/jpm;image/jpeg;video/jpeg;application/vnd.kahootz;application/vnd.chipnuts.karaoke-mmd;application/vnd.kde.karbon;aplication/vnd.kde.kchart;application/vnd.kde.kformula;application/vnd.kde.kivio;application/vnd.kde.kontour;application/vnd.kde.kpresenter;application/vnd.kde.kspread;application/vnd.kde.kword;application/vnd.kenameaapp;applicatin/vnd.kidspiration;application/vnd.kinar;application/vnd.kodak-descriptor;application/vnd.las.las+xml;application/x-latex;application/vnd.llamagraphics.life-balance.desktop;application/vnd.llamagraphics.life-balance.exchange+xml;application/vnd.jam;application/vnd.lotus-1-2-3;application/vnd.lotus-approach;application/vnd.lotus-freelance;application/vnd.lotus-notes;application/vnd.lotus-organizer;application/vnd.lotus-screencam;application/vnd.lotus-wordro;audio/vnd.lucent.voice;audio/x-mpegurl;video/x-m4v;application/mac-binhex40;application/vnd.macports.portpkg;application/vnd.osgeo.mapguide.package;application/marc;application/marcxml+xml;application/mxf;application/vnd.wolfrm.player;application/mathematica;application/mathml+xml;application/mbox;application/vnd.medcalcdata;application/mediaservercontrol+xml;application/vnd.mediastation.cdkey;application/vnd.mfer;application/vnd.mfmp;model/mesh;appliation/mads+xml;application/mets+xml;application/mods+xml;application/metalink4+xml;application/vnd.ms-powerpoint.template.macroenabled.12;application/vnd.ms-word.document.macroenabled.12;application/vnd.ms-word.template.macroenabed.12;application/vnd.mcd;application/vnd.micrografx.flo;application/vnd.micrografx.igx;application/vnd.eszigno3+xml;application/x-msaccess;video/x-ms-asf;application/x-msdownload;application/vnd.ms-artgalry;application/vnd.ms-ca-compressed;application/vnd.ms-ims;application/x-ms-application;application/x-msclip;image/vnd.ms-modi;application/vnd.ms-fontobject;application/vnd.ms-excel;application/vnd.ms-excel.addin.macroenabled.12;application/vnd.ms-excelsheet.binary.macroenabled.12;application/vnd.ms-excel.template.macroenabled.12;application/vnd.ms-excel.sheet.macroenabled.12;application/vnd.ms-htmlhelp;application/x-mscardfile;application/vnd.ms-lrm;application/x-msmediaview;aplication/x-msmoney;application/vnd.openxmlformats-officedocument.presentationml.presentation;application/vnd.openxmlformats-officedocument.presentationml.slide;application/vnd.openxmlformats-officedocument.presentationml.slideshw;application/vnd.openxmlformats-officedocument.presentationml.template;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;application/vnd.openxmlformats-officedocument.spreadsheetml.template;application/vnd.openxmformats-officedocument.wordprocessingml.document;application/vnd.openxmlformats-officedocument.wordprocessingml.template;application/x-msbinder;application/vnd.ms-officetheme;application/onenote;audio/vnd.ms-playready.media.pya;vdeo/vnd.ms-playready.media.pyv;application/vnd.ms-powerpoint;application/vnd.ms-powerpoint.addin.macroenabled.12;application/vnd.ms-powerpoint.slide.macroenabled.12;application/vnd.ms-powerpoint.presentation.macroenabled.12;appliation/vnd.ms-powerpoint.slideshow.macroenabled.12;application/vnd.ms-project;application/x-mspublisher;application/x-msschedule;application/x-silverlight-app;application/vnd.ms-pki.stl;application/vnd.ms-pki.seccat;application/vn.visio;video/x-ms-wm;audio/x-ms-wma;audio/x-ms-wax;video/x-ms-wmx;application/x-ms-wmd;application/vnd.ms-wpl;application/x-ms-wmz;video/x-ms-wmv;video/x-ms-wvx;application/x-msmetafile;application/x-msterminal;application/msword;application/x-mswrite;application/vnd.ms-works;application/x-ms-xbap;application/vnd.ms-xpsdocument;audio/midi;application/vnd.ibm.minipay;application/vnd.ibm.modcap;application/vnd.jcp.javame.midlet-rms;application/vnd.tmobile-ivetv;application/x-mobipocket-ebook;application/vnd.mobius.mbk;application/vnd.mobius.dis;application/vnd.mobius.plc;application/vnd.mobius.mqy;application/vnd.mobius.msl;application/vnd.mobius.txf;application/vnd.mobius.daf;tex/vnd.fly;application/vnd.mophun.certificate;application/vnd.mophun.application;video/mj2;audio/mpeg;video/vnd.mpegurl;video/mpeg;application/mp21;audio/mp4;video/mp4;application/mp4;application/vnd.apple.mpegurl;application/vnd.msician;application/vnd.muvee.style;application/xv+xml;application/vnd.nokia.n-gage.data;application/vnd.nokia.n-gage.symbian.install;application/x-dtbncx+xml;application/x-netcdf;application/vnd.neurolanguage.nlu;application/vnd.na;application/vnd.noblenet-directory;application/vnd.noblenet-sealer;application/vnd.noblenet-web;application/vnd.nokia.radio-preset;application/vnd.nokia.radio-presets;text/n3;application/vnd.novadigm.edm;application/vnd.novadim.edx;application/vnd.novadigm.ext;application/vnd.flographit;audio/vnd.nuera.ecelp4800;audio/vnd.nuera.ecelp7470;audio/vnd.nuera.ecelp9600;application/oda;application/ogg;audio/ogg;video/ogg;application/vnd.oma.dd2+xml;applicatin/vnd.oasis.opendocument.text-web;application/oebps-package+xml;application/vnd.intu.qbo;application/vnd.openofficeorg.extension;application/vnd.yamaha.openscoreformat;audio/webm;video/webm;application/vnd.oasis.opendocument.char;application/vnd.oasis.opendocument.chart-template;application/vnd.oasis.opendocument.database;application/vnd.oasis.opendocument.formula;application/vnd.oasis.opendocument.formula-template;application/vnd.oasis.opendocument.grapics;application/vnd.oasis.opendocument.graphics-template;application/vnd.oasis.opendocument.image;application/vnd.oasis.opendocument.image-template;application/vnd.oasis.opendocument.presentation;application/vnd.oasis.opendocumen.presentation-template;application/vnd.oasis.opendocument.spreadsheet;application/vnd.oasis.opendocument.spreadsheet-template;application/vnd.oasis.opendocument.text;application/vnd.oasis.opendocument.text-master;application/vnd.asis.opendocument.text-template;image/ktx;application/vnd.sun.xml.calc;application/vnd.sun.xml.calc.template;application/vnd.sun.xml.draw;application/vnd.sun.xml.draw.template;application/vnd.sun.xml.impress;application/vnd.sun.xl.impress.template;application/vnd.sun.xml.math;application/vnd.sun.xml.writer;application/vnd.sun.xml.writer.global;application/vnd.sun.xml.writer.template;application/x-font-otf;application/vnd.yamaha.openscoreformat.osfpvg+xml;application/vnd.osgi.dp;application/vnd.palm;text/x-pascal;application/vnd.pawaafile;application/vnd.hp-pclxl;application/vnd.picsel;image/x-pcx;image/vnd.adobe.photoshop;application/pics-rules;image/x-pict;application/x-chat;aplication/pkcs10;application/x-pkcs12;application/pkcs7-mime;application/pkcs7-signature;application/x-pkcs7-certreqresp;application/x-pkcs7-certificates;application/pkcs8;application/vnd.pocketlearn;image/x-portable-anymap;image/-portable-bitmap;application/x-font-pcf;application/font-tdpfr;application/x-chess-pgn;image/x-portable-graymap;image/png;image/x-portable-pixmap;application/pskc+xml;application/vnd.ctc-posml;application/postscript;application/xfont-type1;application/vnd.powerbuilder6;application/pgp-encrypted;application/pgp-signature;application/vnd.previewsystems.box;application/vnd.pvi.ptid1;application/pls+xml;application/vnd.pg.format;application/vnd.pg.osasli;tex/prs.lines.tag;application/x-font-linux-psf;application/vnd.publishare-delta-tree;application/vnd.pmi.widget;application/vnd.quark.quarkxpress;application/vnd.epson.esf;application/vnd.epson.msf;application/vnd.epson.ssf;applicaton/vnd.epson.quickanime;application/vnd.intu.qfx;video/quicktime;application/x-rar-compressed;audio/x-pn-realaudio;audio/x-pn-realaudio-plugin;application/rsd+xml;application/vnd.rn-realmedia;application/vnd.realvnc.bed;applicatin/vnd.recordare.musicxml;application/vnd.recordare.musicxml+xml;application/relax-ng-compact-syntax;application/vnd.data-vision.rdz;application/rdf+xml;application/vnd.cloanto.rp9;application/vnd.jisp;application/rtf;text/richtex;application/vnd.route66.link66+xml;application/rss+xml;application/shf+xml;application/vnd.sailingtracker.track;image/svg+xml;application/vnd.sus-calendar;application/sru+xml;application/set-payment-initiation;application/set-reistration-initiation;application/vnd.sema;application/vnd.semd;application/vnd.semf;application/vnd.seemail;application/x-font-snf;application/scvp-vp-request;application/scvp-vp-response;application/scvp-cv-request;application/svp-cv-response;application/sdp;text/x-setext;video/x-sgi-movie;application/vnd.shana.informed.formdata;application/vnd.shana.informed.formtemplate;application/vnd.shana.informed.interchange;application/vnd.shana.informed.package;application/thraud+xml;application/x-shar;image/x-rgb;application/vnd.epson.salt;application/vnd.accpac.simply.aso;application/vnd.accpac.simply.imp;application/vnd.simtech-mindmapper;application/vnd.commonspace;application/vnd.ymaha.smaf-audio;application/vnd.smaf;application/vnd.yamaha.smaf-phrase;application/vnd.smart.teacher;application/vnd.svd;application/sparql-query;application/sparql-results+xml;application/srgs;application/srgs+xml;application/sml+xml;application/vnd.koan;text/sgml;application/vnd.stardivision.calc;application/vnd.stardivision.draw;application/vnd.stardivision.impress;application/vnd.stardivision.math;application/vnd.stardivision.writer;application/vnd.tardivision.writer-global;application/vnd.stepmania.stepchart;application/x-stuffit;application/x-stuffitx;application/vnd.solent.sdkm+xml;application/vnd.olpc-sugar;audio/basic;application/vnd.wqd;application/vnd.symbian.install;application/smil+xml;application/vnd.syncml+xml;application/vnd.syncml.dm+wbxml;application/vnd.syncml.dm+xml;application/x-sv4cpio;application/x-sv4crc;application/sbml+xml;text/tab-separated-values;image/tiff;application/vnd.to.intent-module-archive;application/x-tar;application/x-tcl;application/x-tex;application/x-tex-tfm;application/tei+xml;text/plain;application/vnd.spotfire.dxp;application/vnd.spotfire.sfs;application/timestamped-data;applicationvnd.trid.tpt;application/vnd.triscape.mxs;text/troff;application/vnd.trueapp;application/x-font-ttf;text/turtle;application/vnd.umajin;application/vnd.uoml+xml;application/vnd.unity;application/vnd.ufdl;text/uri-list;application/nd.uiq.theme;application/x-ustar;text/x-uuencode;text/x-vcalendar;text/x-vcard;application/x-cdlink;application/vnd.vsf;model/vrml;application/vnd.vcx;model/vnd.mts;model/vnd.vtu;application/vnd.visionary;video/vnd.vivo;applicatin/ccxml+xml,;application/voicexml+xml;application/x-wais-source;application/vnd.wap.wbxml;image/vnd.wap.wbmp;audio/x-wav;application/davmount+xml;application/x-font-woff;application/wspolicy+xml;image/webp;application/vnd.webturb;application/widget;application/winhlp;text/vnd.wap.wml;text/vnd.wap.wmlscript;application/vnd.wap.wmlscriptc;application/vnd.wordperfect;application/vnd.wt.stf;application/wsdl+xml;image/x-xbitmap;image/x-xpixmap;image/x-xwindowump;application/x-x509-ca-cert;application/x-xfig;application/xhtml+xml;application/xml;application/xcap-diff+xml;application/xenc+xml;application/patch-ops-error+xml;application/resource-lists+xml;application/rls-services+xml;aplication/resource-lists-diff+xml;application/xslt+xml;application/xop+xml;application/x-xpinstall;application/xspf+xml;application/vnd.mozilla.xul+xml;chemical/x-xyz;text/yaml;application/yang;application/yin+xml;application/vnd.ul;application/zip;application/vnd.handheld-entertainment+xml;application/vnd.zzazz.deck+xml;csv/comma-separated-values")
    # https://www.lifewire.com/firefox-about-config-entry-browser-445707
    # profile.set_preference('browser.download.folderList', 1) # downloads folder
    # profile.set_preference('browser.download.manager.showWhenStarting', False)
    # profile.set_preference('browser.helperApps.alwaysAsk.force', False)
    # # profile.set_preference('browser.download.dir', '/tmp')
    # profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    # profile.set_preference('browser.helperApps.neverAsk.saveToDisk', '*')
    driver = webdriver.Firefox(profile, executable_path='/home/nate/geckodriver')

    # prevent broken pipe errors
    # https://stackoverflow.com/a/13974451/4549682
    driver.implicitly_wait(5)
    # barchart.com takes a long time to load; I think it's ads
    driver.set_page_load_timeout(10)
    return driver


def sign_in(driver, source='barchart.com'):
    if source == 'investing.com':
        sign_in_investing_com(driver)
    elif source == 'barchart.com':
        sign_in_barchart_com(driver)


def sign_in_investing_com(driver):
    username = os.environ.get('investing_username')
    password = os.environ.get('investing_password')
    if username is None or password is None:
        print('add email and pass to bashrc!! exiting.')
        return

    try:
        driver.get('https://www.investing.com')
    except TimeoutException:
        pass

    # if popup appears, close it -- seems to only happen when not signed in
    # seems to only appear after moving mouse around on page and waiting a sec
    # driver.execute_script("document.getElementsByClassName('popupCloseIcon')[0].click()")
    # from selenium.webdriver.common.action_chains import ActionChains
    # hoverover = ActionChains(driver).move_to_element(element1).perform()
    # time.sleep(5)
    # popup = driver.find_elements_by_id('PromoteSignUpPopUp')
    # if popup is not None:
    #     close_icon = popup.find_element_by_class_name('popupCloseIcon')
    #     close_icon.click()

    driver.find_element_by_xpath("//*[text()='Sign In']").click()
    driver.find_element_by_id('loginFormUser_email').send_keys(username)
    driver.find_element_by_id('loginForm_password').send_keys(password)
    # click the "Sign In" button
    popup = driver.find_element_by_id('loginPopup')
    time.sleep(1.27 + np.random.random())
    try:
        popup.find_element_by_link_text('Sign In').click()
    except TimeoutException:
        pass


def sign_in_barchart_com(driver):
    driver.get('https://www.barchart.com/login')
    email = os.environ.get('barchart_username')
    password = os.environ.get('barchart_pass')
    if email is None or password is None:
        print('add email and pass to bashrc!! exiting.')
        return

    try:
        driver.find_element_by_name('email').send_keys(email)
        driver.find_element_by_name('password').send_keys(password)
        time.sleep(1.2 + np.random.random())
    except TypeError:
        close = driver.find_elements_by_class_name('form-close')
        for c in close:
            try:
                c.click()
            except ElementNotInteractableException:
                continue
    try:
        driver.find_element_by_xpath('//button[text()="Log In"]').click()
    except TimeoutException:
        pass
    except ElementClickInterceptedException:
        # classname: reveal-modal-bg fade in
        driver.find_element_by_xpath('/html/body/div[9]/div/div/div[3]/div/div[1]/div/a').click()
        time.sleep(2)
        try:
            driver.find_element_by_xpath('//button[text()="Log In"]').click()
        except TimeoutException:
            pass


def wait_for_data_download(filename=FILEPATH + 'S&P 600 Components.csv'):
    """
    waits for a file (filename) to exist; when it does, ends waiting
    """
    while not os.path.exists(filename):
        time.sleep(0.3)

    return


def check_if_files_exist(source='barchart.com'):
    """
    """
    data_list = ['price', 'performance', 'technical', 'fundamental']

    latest_market_date = get_last_open_trading_day()
    # check if todays data has already been downloaded
    latest_date = cu.get_latest_daily_date(source=source)
    if latest_date is None:
        return False

    latest_date = latest_date.strftime('%Y-%m-%d')
    if latest_date == latest_market_date:
        # check that all 4 files are there
        for d in data_list:
            if not os.path.exists(FILEPATH + '{}/sp600_{}_'.format(source, d) + latest_market_date + '.csv'):
                return False

        print("latest data is already downloaded")
        return True

    return False


def check_if_index_files_exist(index='IJR'):
    latest_market_date = get_last_open_trading_day()
    latest_index_date = cu.get_latest_index_date(index)
    if latest_index_date is None:
        print('no files exist for ' + index)
        return False

    latest_index_date = latest_index_date.strftime('%Y-%m-%d')
    if latest_index_date == latest_market_date:
        # print('latest data already downloaded for ' + index)
        return True
    else:
        # print('data not up to date for ' + index)
        return False


def download_sp600_data(driver, source='barchart.com'):
    """
    downloads sp600 data from investing.com or barchart.com
    """
    if check_if_files_exist(source=source):
        return

    print('data not up to date for {}; downloading'.format(source))

    if source == 'investing.com':
        download_investing_com(driver)
    elif source == 'barchart.com':
        download_barchart_com(driver)


def download_investing_com(driver):
    try:
        driver.get('https://www.investing.com/indices/s-p-600-components')
    except TimeoutException:
        pass

    data_list = ['price', 'performance', 'technical', 'fundamental']
    latest_market_date = get_last_open_trading_day()

    for d, next_d in zip(data_list, data_list[1:] + [None]):
        print('downloading {} data...'.format(d))
        dl_link = driver.find_element_by_class_name('js-download-index-component-data')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", dl_link)
        time.sleep(0.23)
        # need to use alt+click to download without prompt
        # set the option browser.altClickSave to true in config:
        # https://stackoverflow.com/questions/36338653/python-selenium-actionchains-altclick
        # https://superuser.com/a/1009706/435890
        try:
            # ActionChains(driver).key_down(Keys.ALT).click(dl_link).perform()
            # ActionChains(driver).key_up(Keys.ALT).perform()
            dl_link.click()
        except ElementClickInterceptedException:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.13)
            # ActionChains(driver).key_down(Keys.ALT).click(dl_link).perform()
            # ActionChains(driver).key_up(Keys.ALT).perform()
            dl_link.click()

        if next_d is not None:
            try:
                next_link = driver.find_element_by_id('filter_{}'.format(next_d))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", next_link)
                next_link.click()
            except ElementClickInterceptedException:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(0.24)
                driver.find_element_by_id('filter_{}'.format(next_d)).click()

        time.sleep(1.57 + np.random.random())
        wait_for_data_download()
        shutil.move(FILEPATH + 'S&P 600 Components.csv', FILEPATH + 'investing.com/sp600_{}_'.format(d) + latest_market_date + '.csv')


def download_barchart_com(driver):
    # TODO: name file as last open trading day if downloaded a day later
    # e.g. downloaded during the weekend
    # not using todays_date anymore, leaving in for referenc
    # todays_date = datetime.datetime.today().strftime('%Y-%m-%d')
    latest_market_date = get_last_open_trading_day()
    # date to match barchart downloaded filename
    todays_date_bc = datetime.datetime.today().strftime('%m-%d-%Y')
    # need todays date EST for download filename
    tz = pytz.timezone('US/Eastern')
    todays_date_eastern = datetime.datetime.now(tz).strftime('%m-%d-%Y')
    data_list = ['price', 'technical', 'performance', 'fundamental']
    link_list = ['main', 'technical', 'performance', 'fundamental']
    for link, d in zip(link_list, data_list):
        try:
            driver.get('https://www.barchart.com/stocks/indices/sp/sp600?viewName=' + link)
        except TimeoutException:
            pass

        driver.find_element_by_class_name('toolbar-button.download').click()
        filename = FILEPATH + 'sp-600-index-{}.csv'.format(todays_date_eastern)
        print('waiting for...' + filename)
        wait_for_data_download(filename)
        filepath_dst = FILEPATH + 'barchart.com/sp600_{}_'.format(d) + latest_market_date + '.csv'
        shutil.move(filename, filepath_dst)
        time.sleep(1.1 + np.random.random())


def download_ijr_holdings(driver):
    """
    gets csv from iShares SP600 ETF, IJR
    """
    print('downloading IJR data')
    latest_market_date = get_last_open_trading_day()

    driver.get('https://www.ishares.com/us/products/239774/ishares-core-sp-smallcap-etf')
    driver.find_element_by_link_text('Detailed Holdings and Analytics').click()

    # move downloaded file
    datapath = FILEPATH + 'index_funds/IJR/'
    if not os.path.exists(datapath): (make_dirs(datapath))
    src_filename = FILEPATH + 'IJR_holdings.csv'
    wait_for_data_download(src_filename)
    dst_filename =  FILEPATH + 'IJR_holdings_' + latest_market_date + '.csv'
    shutil.move(src_filename, dst_filename)


def download_sly_holdings(driver):
    """
    gets csv from SPDY SP600 ETF, SLY
    """
    print('downloading SLY data')
    latest_market_date = get_last_open_trading_day()

    driver.get('https://us.spdrs.com/en/etf/spdr-sp-600-small-cap-etf-SLY')
    driver.find_element_by_xpath('/html/body/main/article/div[3]/ul/li[3]/a').click()
    driver.find_element_by_xpath('/html/body/main/article/div[4]/div[3]/div[1]/div[1]/section/div[2]/a').click()

    # TODO: refactor this into a function
    datapath = FILEPATH + 'index_funds/SLY/'
    if not os.path.exists(datapath): (make_dirs(datapath))
    src_filename = FILEPATH + 'SLY_All_Holdings.xls'
    wait_for_data_download(src_filename)
    dst_filename =  FILEPAHT + 'SLY_holdings_' + latest_market_date + '.xls'
    shutil.move(src_filename, dst_filename)
    # sometimes source file seems to stick around...
    if os.path.exists(src_filename):
        os.remove(src_filename)


def download_vioo_holdings(driver):
    """
    gets csv from Vanguard SP600 ETF, VIOO

    gives weird Content-Type of csv/comma-separated-values
    """
    print('downloading VIOO data')
    latest_market_date = get_last_open_trading_day()

    # started here and went to "Holding details" link
    #driver.get('https://institutional.vanguard.com/VGApp/iip/site/institutional/investments/productoverview?fundId=3345')
    driver.set_page_load_timeout(20)  # takes long to load
    try:
        driver.get('https://institutional.vanguard.com/VGApp/iip/site/institutional/investments/portfoliodetails?fundId=3345&compositionTabBox=1#hold')
    except TimeoutException:
        pass

    driver.set_page_load_timeout(10)

    # sometimes need to try again after waiting a few seconds
    try:
        try:
            driver.find_element_by_link_text('Export data').click()
        except TimeoutException:
            pass
    except NoSuchElementException:
        time.sleep(2.372)
        try:
            driver.find_element_by_link_text('Export data').click()
        except TimeoutException:
            pass

    # TODO: refactor this into a function
    datapath = FILEPATH + 'index_funds/VIOO/'
    if not os.path.exists(datapath): (make_dirs(datapath))
    src_filename = FILEPATH + 'ProductDetailsHoldings_S&P_Small-Cap_600_ETF.csv'
    wait_for_data_download(src_filename)
    dst_filename =  FILEPATH + 'VIOO_holdings_' + latest_market_date + '.csv'
    shutil.move(src_filename, dst_filename)


def daily_updater(driver):
    """
    checks if any new files to download, if so, downloads them
    """
    def dl_source(source):
        print('downloading update for ' + source)
        sign_in(driver, source=source)
        download_sp600_data(driver, source=source)

    def dl_idx(index):
        print('downloading update for ' + index)
        if index == 'IJR':
            download_ijr_holdings(driver)
        elif index == 'SLY':
            download_sly_holdings(driver)
        elif index == 'VIOO':
            download_vioo_holdings(driver)

    while True:
        try:
            today_utc = pd.to_datetime('now')
            today_ny = datetime.datetime.now(pytz.timezone('America/New_York'))
            is_trading_day = check_if_today_trading_day()
            for source in ['barchart.com', 'investing.com']:
                if not check_if_files_exist(source=source):
                    # if files not there, latest files are not today, and today is not a trading day...
                    up_to_date = today_ny.date() == cu.get_latest_daily_date(source).date()
                    if not up_to_date and not is_trading_day:
                        dl_source(source)
                    elif not up_to_date and today_ny.hour >= 20:
                        dl_source(source)

            for index in ['IJR', 'SLY', 'VIOO']:
                if not check_if_index_files_exist(index):
                    latest_index_date = cu.get_latest_index_date(index)
                    up_to_date = latest_index_date.date() == today_ny.date()
                    if not up_to_date and not is_trading_day:
                        dl_idx(index)
                    elif not up_to_date and today_ny.hour >= 20:
                        dl_idx(index)

            print('sleeping 1h...')
            time.sleep(3600)
        except Exception as e:
            print(e)
            print(traceback.print_tb(e.__traceback__))
            driver.quit()
            driver = setup_driver()


if __name__ == '__main__':
    driver = setup_driver()
    daily_updater(driver)


    # for source in ['barchart.com', 'investing.com']:
    #     if not check_if_files_exist(source=source):
    #         sign_in(driver, source=source)
    #         download_sp600_data(driver, source=source)
